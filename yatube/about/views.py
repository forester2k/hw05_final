# about/views.py

# from django.shortcuts import render
from django.views.generic.base import TemplateView

# Описать класс AboutAuthorView для страницы about/author

# Описать класс AboutTechView для страницы about/tech


class AboutAuthorView(TemplateView):
    # В переменной template_name обязательно указывается имя шаблона,
    # на основе которого будет создана возвращаемая страница
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    # В переменной template_name обязательно указывается имя шаблона,
    # на основе которого будет создана возвращаемая страница
    template_name = 'about/tech.html'
