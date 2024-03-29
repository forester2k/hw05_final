# posts/tests/tests_views.py
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms

from ..models import Follow, Group, Post

User = get_user_model()
page_len = settings.ITEMS_ON_PAGE

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.other_user = User.objects.create_user(username='StasBasov')
        cls.user = User.objects.create_user(username='bifbigauth')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='Test_slug_1',
            description='Тестовое описание 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='Test_slug_2',
            description='Тестовое описание 2',
        )
        cls.user_post = Post.objects.create(
            author=cls.other_user,
            group=cls.group_1,
            text='Тестовый текст, и он должен не короток быть...',
            image=uploaded,
        )
        # Создаем (13+5)=18 тестовых постов
        lst_1 = [Post(
            author=cls.user,
            group=cls.group_1,
            text=f'{i}. 1 Тестовый текст...',
            image=uploaded,
        ) for i in range(11, 24)]
        lst_2 = [Post(
            author=cls.user,
            group=cls.group_2,
            text=f'{i}. 2 Тестовый текст...',
            image=uploaded,
        ) for i in range(31, 36)]
        Post.objects.bulk_create(lst_1 + lst_2)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями: создание, удаление,
        # копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверка контекста в отдельной процедуре
    def _check_context(self, response, last_post):
        if 'post' in response.context:
            first_object = response.context['post']
        else:
            first_object = response.context['page_obj'][0]
        post_author = first_object.author
        post_group = first_object.group
        post_text = first_object.text
        post_image = first_object.image
        self.assertEqual(post_author, last_post.author)
        self.assertEqual(post_group, last_post.group)
        self.assertEqual(post_text, last_post.text)
        self.assertEqual(post_image, last_post.image)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post_id = Post.objects.filter(author=self.user)[0].id
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (
                reverse(
                    'posts:group_posts',
                    kwargs={'slug': self.group_1.slug}
                )
            ): 'posts/group_list.html',
            (
                reverse('posts:profile', kwargs={'username': self.user})
            ): 'posts/profile.html',
            (
                reverse('posts:post_detail', kwargs={'post_id': post_id})
            ): 'posts/post_detail.html',
            (
                reverse('posts:post_edit', kwargs={'post_id': post_id})
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем, что словарь context страницы index
    # в первом элементе списка page_obj содержит ожидаемые значения
    def test_index_list_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        last_post = Post.objects.all()[0]
        self._check_context(response, last_post)

    def test_index_first_page_contains_ten_records(self):
        """Первая страница index содержит тербуемое количество постов"""
        response = self.authorized_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице index.
        self.assertEqual(len(response.context['page_obj']), page_len)

    def test_index_second_page_contains_nine_records(self):
        """Последняя страница index содержит тербуемое количество постов"""
        # Проверка: количество постов на второй странице index.
        posts_count = Post.objects.count()
        last_block_len = posts_count % page_len
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), last_block_len)

    # Проверяем, что словарь context страницы /group/<slug>/
    # в первом элементе списка page_obj содержит ожидаемые значения
    def test_group_list_page_show_correct_context(self):
        """Шаблон /group/<slug>/ сформирован с правильным контекстом."""
        group_3 = Group.objects.create(
            title='Тестовая группа 3',
            slug='Test_slug_3',
            description='Тестовое описание 3',
        )
        new_post = Post.objects.create(
            author=self.other_user,
            group=group_3,
            text='Проверки группы пост...',
        )
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': group_3.slug})
        )
        self._check_context(response, new_post)

    def test_group_first_page_contains_ten_records(self):
        """Первая страница /group/<slug>/
        содержит тербуемое количество постов"""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group_1.slug})
        )
        self.assertEqual(len(response.context['page_obj']), page_len)

    def test_group_second_page_contains_four_records(self):
        """Последняя страница /group/<slug>/
        содержит тербуемое количество постов"""
        using_group = Group.objects.get(slug=self.group_1.slug)
        posts_count = Post.objects.filter(group=using_group).count()
        last_block_len = posts_count % page_len
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group_1.slug})
            + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), last_block_len)

    # Проверяем, что словарь context страницы profile/<username>/
    # в первом элементе списка page_obj содержит ожидаемые значения
    def test_profile_page_show_correct_context(self):
        """Шаблон profile/<username>/ сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        using_author = User.objects.get(username=self.user)
        last_post = Post.objects.filter(author=using_author)[0]
        posts_count = Post.objects.filter(author=using_author).count()
        self._check_context(response, last_post)
        self.assertEqual(response.context['page_count'], posts_count)
        self.assertEqual(response.context['author'], using_author)

    def test_profil_first_page_contains_ten_records(self):
        """Первая страница profile/<username>/
        содержит тербуемое количество постов"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(len(response.context['page_obj']), page_len)

    def test_profil_second_page_contains_three_records(self):
        """Последняя страница profile/<username>/
        содержит тербуемое количество постов"""
        using_author = User.objects.get(username=self.user)
        posts_count = Post.objects.filter(author=using_author).count()
        last_block_len = posts_count % page_len
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
            + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), last_block_len)

    # Проверяем, что словарь context страницы profile/<username>/
    # в первом элементе списка page_obj содержит ожидаемые значения
    def test_profile_page_show_correct_context(self):
        """Шаблон profile/<username>/ сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.other_user})
        )
        using_author = User.objects.get(username=self.other_user)
        last_post = Post.objects.filter(author=using_author)[0]
        posts_count = Post.objects.filter(author=using_author).count()
        self._check_context(response, last_post)
        self.assertEqual(response.context['page_count'], posts_count)
        self.assertEqual(response.context['author'], using_author)

    # Проверяем, что словарь context страницы post_detail/<post_id>/
    # содержит ожидаемые значения
    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail/<post_id>/ сформирован с правильным контекстом"""
        using_author = User.objects.get(username=self.user)
        last_post = Post.objects.filter(author=using_author)[0]
        posts_count = Post.objects.filter(author=using_author).count()
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': last_post.id})
        )
        self._check_context(response, last_post)
        self.assertEqual(response.context['post_count'], posts_count)

    # Проверяем, что словарь context страницы post_edit/<post_id>/edit/
    # содержит ожидаемые значения
    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit/<post_id>/edit/ с правильным контекстом."""
        using_author = User.objects.get(username=self.user)
        last_post = Post.objects.filter(author=using_author)[0]
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': last_post.id})
        )
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        # Проверяем, что типы полей формы в context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['is_edit'], True)

    # Проверяем, что словарь context страницы create/
    # содержит ожидаемые значения
    def test_post_create_page_show_correct_context(self):
        """Шаблон create/ сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # Проверяем, что пост с указанной группой
    # не попадает в другую группу
    def test_post_not_in_another_group(self):
        """Пост не попадает в другую группу."""
        using_group = Group.objects.get(slug=self.group_1.slug)
        unusing_group = Group.objects.get(slug=self.group_2.slug)
        last_post = Post.objects.filter(group=using_group)[0]
        unusing_posts = Post.objects.filter(group=unusing_group)
        self.assertNotIn(last_post, unusing_posts)

    # Проверяем кеширование
    def test_index_cache(self):
        """Главная страница кешируется"""
        # Смотрим на страницу
        response = self.authorized_client.get(reverse('posts:index'))
        content_1 = response.content
        # Создаем пост
        self.post_for_cach = Post.objects.create(
            author=self.user,
            group=self.group_1,
            text='Пост для проверки кеша...',
        )
        # Смотрим на страницу, там не должно ничего измениться
        response = self.authorized_client.get(reverse('posts:index'))
        content_2 = response.content
        self.assertEqual(content_1, content_2)
        # Чистим кеш
        cache.clear()
        # Смотрим на страницу, она должна измениться
        response = self.authorized_client.get(reverse('posts:index'))
        content_3 = response.content
        self.assertNotEqual(content_1, content_3)
        # Убираем за собой
        self.post_for_cach.delete()

    # Авторизованный пользователь может подписываться
    # на других пользователей.
    def test_user_following(self):
        """Авторизованный пользователь может подписываться."""
        # Подписок в базе
        follow_count_start = Follow.objects.count()
        # Подписка
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.other_user})
        )
        # Подписок стало
        follow_count_end = Follow.objects.count()
        self.assertEqual(follow_count_start + 1, follow_count_end)
        # Достаем подписку
        follow = Follow.objects.all()[0]
        # Проверяем соответствие
        self.assertEqual(self.user, follow.user)
        self.assertEqual(self.other_user, follow.author)
        follow.delete()

    # Авторизованный пользователь может отписываться
    # от других пользователей.
    def test_user_unfolowing(self):
        """Авторизованный пользователь может отписываться."""
        Follow.objects.create(
            user=self.user,
            author=self.other_user
        )
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.other_user})
        )
        is_follow = Follow.objects.filter(
            user=self.user,
            author=self.other_user
        ).exists()
        self.assertFalse(is_follow)

    # Новая запись пользователя появляется в ленте тех,
    # кто на него подписан.
    def test_folower_see_new_post(self):
        """Новый пост виден в ленте у подписчика."""
        # Создаем свежего юзера
        fresh_user = User.objects.create_user(username='IamFresh')
        fresh_author = User.objects.create_user(username='IamFreshAuthor')
        # Создаем подписку
        Follow.objects.create(user=fresh_user, author=fresh_author)
        # Создаем пост
        new_post = Post.objects.create(
            author=fresh_author,
            group=self.group_1,
            text='Подписки проверки пост...',
        )
        # Запрашиваем ленту
        self.authorized_fresh = Client()
        self.authorized_fresh.force_login(fresh_user)
        response = self.authorized_fresh.get(reverse('posts:follow_index'))
        # Проверяем соответствие контекста
        self._check_context(response, new_post)
        new_post.delete()

    # Новая запись пользователя не появляется в ленте тех,
    # кто на него не подписан.
    def test_unfolower_dont_see_new_post(self):
        """Новый пост не виден в ленте у неподписавшегося."""
        # Создаем свежего юзера
        fresh_user_too = User.objects.create_user(username='IamFreshToo')
        # Создаем пост
        new_post = Post.objects.create(
            author=self.other_user,
            group=self.group_1,
            text='Не подписки проверки пост...',
        )
        # Запрашиваем ленту
        self.authorized_fresh_too = Client()
        self.authorized_fresh_too.force_login(fresh_user_too)
        response = self.authorized_fresh_too.get(reverse('posts:follow_index'))
        self.assertEqual(response.context['page_obj'].paginator.count, 0)
        new_post.delete()
