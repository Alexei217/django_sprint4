from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="index"),
    path(
        "posts/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"
    ),
    path(
        "category/<slug:category_slug>/",
        views.CategoryView.as_view(),
        name="category_posts",
    ),
    path(
        "profile/edit/", views.ProfileUpdateView.as_view(), name="edit_profile"
    ),
    path(
        "profile/<str:username>/", views.ProfileView.as_view(), name="profile"
    ),
    path("posts/create/", views.PostCreateView.as_view(), name="create_post"),
    path(
        "posts/<int:pk>/edit/",
        views.PostUpdateView.as_view(),
        name="edit_post",
    ),
    path(
        "posts/<int:pk>/delete/",
        views.PostDeleteView.as_view(),
        name="delete_post",
    ),
    path(
        "posts/<int:pk>/comment/",
        views.CommentCreateView.as_view(),
        name="add_comment",
    ),
    path(
        "posts/<int:post_id>/edit_comment/<int:pk>/",
        views.CommentUpdateView.as_view(),
        name="edit_comment",
    ),
    path(
        "posts/<int:post_id>/delete_comment/<int:pk>/",
        views.CommentDeleteView.as_view(),
        name="delete_comment",
    ),
]
