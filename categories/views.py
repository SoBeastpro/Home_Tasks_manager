"""Представления списка и карточки категорий."""

from html import escape

from django.http import HttpRequest, HttpResponse

from homepage.views import page
from models.categories import find_category_or_none
from models.chores import filter_chores_by_category
from storage import load_categories, load_chores, load_users
from utils import format_date


def _load_data():
    """Загрузить категории и дела из JSON через storage."""
    users = load_users()
    categories = load_categories()
    chores = load_chores(users, categories)
    return categories, chores


def category_list(request: HttpRequest) -> HttpResponse:
    """Показать список категорий из JSON."""
    categories, chores = _load_data()
    if not categories:
        content = "<p>Категории ещё не добавлены.</p>"
    else:
        rows = []
        for category in categories:
            count = len(
                filter_chores_by_category(chores, category.id)
            )
            name = escape(category.name)
            rows.append(
                "<tr>"
                f"<td>{category.id}</td>"
                f'<td><a href="/categories/{category.id}/">{name}</a></td>'
                f"<td>{count}</td>"
                "</tr>"
            )
        content = (
            '<table class="table table-striped table-hover">'
            "<thead><tr>"
            "<th>№</th><th>Название</th><th>Дел</th>"
            "</tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>"
        )
    return HttpResponse(page("Категории", content, active="categories"))


def category_detail(
    request: HttpRequest,
    category_id: int,
) -> HttpResponse:
    """Показать категорию и её дела или страницу 404."""
    categories, chores = _load_data()
    category = find_category_or_none(categories, category_id)
    if category is None:
        content = (
            f"<p>Категория с номером {category_id} не найдена.</p>"
            '<p><a class="btn btn-success" href="/categories/">'
            "К списку категорий</a></p>"
        )
        return HttpResponse(
            page("Категория не найдена", content, active="categories"),
            status=404,
        )
    related = filter_chores_by_category(chores, category.id)
    if not related:
        chores_html = "<p>В этой категории пока нет дел.</p>"
    else:
        items = []
        for chore in related:
            title = escape(chore.title)
            user_name = escape(chore.user.name)
            status_name = escape(str(chore.status))
            due = format_date(chore.due_date)
            items.append(
                "<li class=\"list-group-item\">"
                f'<a href="/chores/{chore.id}/">{title}</a>'
                f" — {user_name}, до {due}, {status_name}"
                "</li>"
            )
        chores_html = (
            '<ul class="list-group">'
            f"{''.join(items)}"
            "</ul>"
        )
    content = f"""
    <p class="lead">Категория №{category.id}</p>
    {chores_html}
    <p class="mt-3">
      <a class="btn btn-outline-success" href="/categories/">
        К списку категорий
      </a>
    </p>
    """
    title = f"Категория: {category.name}"
    return HttpResponse(page(title, content, active="categories"))
