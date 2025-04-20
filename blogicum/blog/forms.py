from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ("author",)
        widgets = {
            "pub_date": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M:%S", attrs={"type": "datetime-local"}
            )
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ("text",)
