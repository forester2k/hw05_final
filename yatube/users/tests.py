# users/tests.py
from users.forms import CreationForm
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserCreateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

    def test_create_task(self):
        """Валидная форма создает нового пользователя """
        users_count = User.objects.count()
        form_data = {
            'first_name': 'TestName',
            'last_name': 'TestSurName',
            'username': 'simplenick',
            'email': 'test@test.ru',
            'password1': 'qaQa1!$4fds',
            'password2': 'qaQa1!$4fds'
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            # data=my_form,
            follow=True
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertRedirects(response, reverse('posts:index'))
