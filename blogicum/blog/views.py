from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from blog.models import Post, Category, User, Comment
from .forms import PostForm, CommentForm
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.contrib.auth import get_user_model

User = get_user_model()

def get_annotated_posts(queryset):
    return queryset.annotate(comment_count=Count("comments"))

def get_published_posts(queryset):
    current_time = timezone.now()
    return queryset.filter(
        Q(is_published=True) &
        Q(pub_date__lte=current_time) &
        Q(category__is_published=True)
    )

def get_visible_posts(queryset, user=None):
    if user and user.is_authenticated:
        return queryset.filter(
            Q(author=user) | 
            Q(is_published=True) &
            Q(pub_date__lte=timezone.now()) &
            Q(category__is_published=True)
        )
    return get_published_posts(queryset)

# Create your views here.
class PostListView(ListView):
    model = Post
    paginate_by = 10

    def get_queryset(self, **kwargs):
        queryset = Post.objects.select_related("category", "location", "author")
        queryset = get_annotated_posts(queryset)
        queryset = get_visible_posts(queryset, self.request.user)
        return queryset.order_by("-pub_date")


class HomePageView(PostListView):
    template_name = "blog/index.html"

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        return queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs["post_id"])

        if not post.is_published and post.author != request.user:
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.select_related("author")
        return context


class CategoryView(PostListView):
    template_name = "blog/category.html"

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        return queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__slug=self.kwargs["category_slug"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        context["category"] = category
        return context


class ProfileView(PostListView):
    template_name = "blog/profile.html"

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        return queryset.filter(author__username=self.kwargs["username"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(User, username=self.kwargs["username"])
        context["profile"] = profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ("username", "first_name", "last_name", "email")
    template_name = "blog/user.html"
    login_url = reverse_lazy("login")

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    login_url = reverse_lazy("login")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    login_url = reverse_lazy("login")

    def form_valid(self, form):
        self.success_url = reverse_lazy(
            "blog:post_detail", kwargs={"post_id": form.instance.id}
        )
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs["post_id"])
        if instance.author != request.user:
            return redirect("blog:post_detail", post_id=instance.pk)
        return super().dispatch(request, *args, **kwargs)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:index")
    pk_url_kwarg = 'post_id'
    login_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs["post_id"])
        if instance.author != request.user:
            return redirect("blog:index")
        return super().dispatch(request, *args, **kwargs)


class CommentView(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    login_url = reverse_lazy("login")


class CommentCreateView(CommentView, CreateView):
    _post = None

    def dispatch(self, request, *args, **kwargs):
        self._post = get_object_or_404(Post, pk=kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self._post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"post_id": self._post.pk})
    
    def get_object(self, queryset=None):
        return get_object_or_404(Comment, pk=self.kwargs.get("pk") or self.kwargs.get("comment_id"))



class CommentChangeView(CommentView):
    template_name = "blog/comment.html"

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs["comment_id"])
        if instance.author != request.user:
            return redirect("blog:post_detail", instance.post.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.object.post.pk}
        )


class CommentUpdateView(CommentChangeView, UpdateView):
    def get_object(self, queryset=None):
        return get_object_or_404(Comment, pk=self.kwargs.get("comment_id"))



class CommentDeleteView(CommentChangeView, DeleteView):
    def get_object(self, queryset=None):
        return get_object_or_404(Comment, pk=self.kwargs.get("comment_id"))
