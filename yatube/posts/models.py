# models.py

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Text',
        help_text='Текст нового поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Group',
        help_text='Группа, к которой будет относиться пост'
    )
    # Поле для картинки (необязательное)
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )
    # Аргумент upload_to указывает директорию,
    # в которую будут загружаться пользовательские файлы.

    class Meta:
        # ordering = ['-pub_date']
        # Если что-то пойдет не так, поменять ордеринг на закомментированный
        ordering = ['-pub_date', '-pk']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        # выводим начало текста поста
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Текст Поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        verbose_name='Текст комментария ',
        help_text='Текст нового поста'
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )


    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=['user', 'author'], name='unique_follow'
                ),
            ]
