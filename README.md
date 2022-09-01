# hw05_final

### О проекте

Данный проект является учебным.
Проект hw05_final  - это небольшая социальная сеть для ведения блогов. Она дает возможность публиковать личные заметки, добавлять к ним фотографии, а также подписываться на других авторов, просматривать их заметки или группы заметок, а также оставлять к ним комментарии.
Целью создания данного проекта было, прежде всего, освоение функционала фреймворка Django.

### Технологический стек

Python 3.7
Django==2.2
Pillow==8.3
pytest==6.2
requests==2.26

### Как запустить проект.

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/forester2k/hw05_final.git
```

```
cd api_yamdb
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


### Как делать запросы:

К проекту по адресу .../redoc/ подключена документация redoc, содержащая сведения по доступным эндпоинтам и примеры запросов.


### Импорт внешних данных в проект:

При необходимости импортировать внешние данные, в проекте реализована команда csv_sql для  заполнения таблиц БД из .csv файлов. Синтаксис команды:

```
python manage.py csv_sql <файл .csv> <название модели>
```



### Под руководством команды Яндекс-Практикума над проектом работали:

- Васильев Кирилл - Разработчик
- Ежов Михаил - Разработчик
- Сосновский Александр - Разработчик
- Тихонов Станислав - Разработчик / Тимлид

