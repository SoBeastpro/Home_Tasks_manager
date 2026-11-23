"""Общие данные шаблонов Home Tasks."""

from categories.models import Category
from chores.models import Chore


def site_context(request) -> dict:
    """Передать название сайта и количество записей в шаблоны."""
    return {
        "site_name": "Home Tasks",
        "categories_count": Category.objects.count(),
        "chores_count": Chore.objects.count(),
    }
