"""Представления списка и карточки категорий."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.categories import find_category_or_none
from models.chores import filter_chores_by_category
from storage import load_categories, load_chores, load_users


def _load_data():
    """Загрузить категории и дела из JSON через storage."""
    users = load_users()
    categories = load_categories()
    chores = load_chores(users, categories)
    return categories, chores


def category_list(request: HttpRequest) -> HttpResponse:
    """Показать список категорий из JSON."""
    categories, chores = _load_data()
    category_items = []
    for category in categories:
        category_items.append(
            {
                "category": category,
                "chore_count": len(
                    filter_chores_by_category(chores, category.id)
                ),
            }
        )
    context = {"category_items": category_items}
    return render(request, "categories/category_list.html", context)


def category_detail(
    request: HttpRequest,
    category_id: int,
) -> HttpResponse:
    """Показать категорию и её дела или страницу 404."""
    categories, chores = _load_data()
    category = find_category_or_none(categories, category_id)
    related = []
    if category is not None:
        related = filter_chores_by_category(chores, category.id)
    context = {
        "category": category,
        "chores": related,
    }
    return render(
        request,
        "categories/category_detail.html",
        context,
        status=404 if category is None else 200,
    )
