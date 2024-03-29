# hw05_final

### О проекте

Данный проект является учебным.
Проект hw05_final  - это небольшая социальная сеть для ведения блогов. Она дает возможность публиковать личные заметки, добавлять к ним фотографии, а также подписываться на других авторов, просматривать их заметки или группы заметок, а также оставлять к ним комментарии. Публикация и редактирование возможно только для авторизованных пользователей. Для того, чтобы не перегружать вывод, в проекте предусмотрена пагинация.
Целью создания данного проекта было, прежде всего, освоение функционала фреймворка Django.

### Технологический стек

- Python 3.7 
- Django 2.2 
- Pillow 8.3
- pytest 6.2
- requests 2.26

### Как запустить проект.

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/forester2k/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Доступный функционал:

Анонимные пользователи могут просматривать:
+ посты
+ информацию о сообществах
+ комментарии

Авторизованные пользователи дополнительно могут:
+ публиковать, редактировать, удалять свои посты
+ публиковать, редактировать, удалять свои  комментарии к постам любого пользователя
+ подписываться на других пользователей и отписываться от них, просматривать посты тех, на кого подписан


### Под руководством команды Яндекс-Практикума над проектом работал:

- Тихонов Станислав - Разработчик

