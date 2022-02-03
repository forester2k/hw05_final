# posts/tests/tests_form.py
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, Comment

User = get_user_model()

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
            author=cls.user,
            group=cls.group_1,
            text='Тестовый текст, и он должен не короток быть...',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями: создание, удаление,
        # копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись Post."""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый текст из формы',
            'group': self.group_1.id,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверяем, что создалась запись с заданными полями
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, Group.objects.get(pk=form_data['group']))
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image, 'posts/' + uploaded.name)

    def test_edit_post(self):
        """Валидная форма изменяет запись Post."""
        post_count = Post.objects.count()
        old_text = self.user_post.text
        old_group = self.user_post.group
        old_author = self.user_post.author
        post_id = self.user_post.id
        new_form = {
            'text': 'Тестовый текст из формы',
            'group': self.group_2.id,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=new_form,
            follow=True
        )
        post = Post.objects.get(id=post_id)
        # Проверяем, что значения в посте изменились
        self.assertNotEqual(old_text, post.text)
        self.assertNotEqual(old_group, post.group)
        self.assertEqual(old_author, post.author)
        # Проверяем, что число постов в базе осталось тем же
        self.assertEqual(Post.objects.count(), post_count)
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post_id})
        )

    def test_not_create_post(self):
        """Неавторизованный пользователь не может создать запись Post."""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст из формы',
            'group': self.group_1.id,
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('posts:post_create')
        )
        # Проверяем, что не изменилось число постов
        self.assertEqual(Post.objects.count(), post_count)

    def test_not_create_comment(self):
        """Неавторизованный пользователь не может написать комментарий."""
        # Подсчитаем количество записей в Comment
        comment_count = Comment.objects.count()
        post_id = self.user_post.id
        form_data = {
            'text': 'Тестовый комментарий от неавторизованного клиента',
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        reverse_1 = reverse('users:login')
        reverse_2 = reverse('posts:add_comment', kwargs={'post_id': post_id})
        self.assertRedirects(response, reverse_1 + '?next=' + reverse_2)
        # Проверяем, что не изменилось число комментов
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_create_comment(self):
        """Валидная форма создает запись Comment."""
        # Подсчитаем количество записей в Comment
        comment_count = Comment.objects.count()
        post_id = self.user_post.id
        form_data = {
            'text': 'Тестовый комментарий от авторизованного клиента',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post_id})
        )
        # Проверяем, увеличилось ли число комментариев
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        # Проверяем, что создалась запись с заданными полями
        comment = Comment.objects.order_by('-created').first()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, Post.objects.get(id=post_id))
        self.assertEqual(comment.author, self.user)
