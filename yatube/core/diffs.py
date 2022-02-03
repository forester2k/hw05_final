# differents.py
from django.conf import settings
from django.core.paginator import Paginator


def page_cuter(request, post_list):
    paginator = Paginator(post_list, settings.ITEMS_ON_PAGE)
    page = request.GET.get('page')
    return paginator.get_page(page)
