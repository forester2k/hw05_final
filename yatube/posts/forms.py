# forms.py
from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        # На основе какой модели создаётся класс формы
        model = Post
        # Укажем, какие поля будут в форме
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        # На основе какой модели создаётся класс формы
        model = Comment
        # Укажем, какие поля будут в форме
        fields = ('text',)
