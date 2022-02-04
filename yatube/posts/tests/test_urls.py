# posts/tests/tests_url.py
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class PostsUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_user = User.objects.create_user(username='StasBasov')
        cls.user = User.objects.create_user(username='bifbigauth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание',
        )
        cls.user_post = Post.objects.create(
            author=cls.other_user,
            group=cls.group,
            text='Тестовый текст, и он должен не короток быть...',
        )
        cls.author_post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст, и он должен не короток быть...',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем общедоступные страницы
    def test_common_url_exists_at_desired_location(self):
        """Страницы доступные любому пользователю."""
        post_id = Post.objects.all()[0].id
        url_names = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
            reverse('posts:post_detail', kwargs={'post_id': post_id}),
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем доступ к несуществующей странице
    def test_not_existing_page(self):
        """Страница /unexisting_page/ недоступна никому"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    # Проверяем доступ к странице /create/
    def test_create_page(self):
        """Страница /create/ доступна авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем доступ к странице /follow/
    def test_follow_page(self):
        """Страница /follow/ доступна авторизованному пользователю"""
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем доступ автора к странице /posts/<post_id>/edit/
    def test_edit_page(self):
        """Страница /posts/<post_id>/edit/ доступна автору"""
        post_id = Post.objects.filter(author=self.user)[0].id
        response = self.authorized_client.get(f'/posts/{post_id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем соответствие шаблонов и url
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post_id = Post.objects.filter(author=self.user)[0].id
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:follow_index'): 'posts/follow.html',
            (
                reverse('posts:group_posts', kwargs={'slug': self.group.slug})
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
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author(self):
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech(self):
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
