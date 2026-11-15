"""Представления дел: данные загружаются через Django ORM."""

from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from categories.models import Category
from chores.models import STATUS_DONE, Chore
from users.models import User


SORT_FIELDS = {
    "date": "due_date",
    "title": "title",
    "user": "user__name",
    "category": "category__name",
    "priority": "-priority",
}
PAGE_SIZE = 5


def _parse_date(value: str):
    """Преобразовать строку YYYY-MM-DD в дату или вернуть None."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _chore_queryset():
    """Вернуть дела вместе с исполнителем и категорией."""
    return Chore.objects.select_related("user", "category")


def chore_list(request: HttpRequest) -> HttpResponse:
    """Показать список дел с поиском, фильтрами и пагинацией."""
    query = request.GET.get("q", "").strip()
    due_date = request.GET.get("date", "").strip()
    category_id = request.GET.get("category", "").strip()
    user_id = request.GET.get("user", "").strip()
    sort = request.GET.get("sort", "date").strip()
    error = None

    chores = _chore_queryset()
    if query:
        chores = chores.filter(
            Q(title__icontains=query) | Q(user__name__icontains=query),
        )
    if due_date:
        selected_date = _parse_date(due_date)
        if selected_date is None:
            error = "Укажите корректную дату."
        else:
            chores = chores.filter(due_date=selected_date)
    if category_id.isdigit():
        chores = chores.filter(category_id=int(category_id))
    if user_id.isdigit():
        chores = chores.filter(user_id=int(user_id))

    sort_field = SORT_FIELDS.get(sort, "due_date")
    chores = chores.order_by(sort_field, "pk")
    page_obj = Paginator(chores, PAGE_SIZE).get_page(
        request.GET.get("page"),
    )
    return render(
        request,
        "chores/chore_list.html",
        {
            "chores": page_obj,
            "page_obj": page_obj,
            "query": query,
            "due_date": due_date,
            "selected_category": category_id,
            "selected_user": user_id,
            "sort": sort,
            "categories": Category.objects.order_by("name"),
            "users": User.objects.order_by("name"),
            "error": error,
        },
    )


def open_chores(request: HttpRequest) -> HttpResponse:
    """Показать невыполненные дела."""
    chores = (
        _chore_queryset()
        .exclude(status=STATUS_DONE)
        .order_by("due_date", "pk")
    )
    return render(
        request,
        "chores/open_list.html",
        {"chores": chores},
    )


def chores_by_date(request: HttpRequest) -> HttpResponse:
    """Найти дела на выбранную дату."""
    due_date = request.GET.get("date", "").strip()
    chores = []
    error = None
    if due_date:
        selected_date = _parse_date(due_date)
        if selected_date is None:
            error = "Укажите корректную дату."
        else:
            chores = (
                _chore_queryset()
                .filter(due_date=selected_date)
                .order_by("-priority", "pk")
            )
    return render(
        request,
        "chores/by_date.html",
        {
            "chores": chores,
            "due_date": due_date,
            "error": error,
        },
    )


def chore_detail(request: HttpRequest, chore_id: int) -> HttpResponse:
    """Показать карточку дела или страницу 404."""
    chore = get_object_or_404(
        _chore_queryset(),
        pk=chore_id,
    )
    return render(
        request,
        "chores/chore_detail.html",
        {
            "chore": chore,
            "deadline_hint": chore.deadline_message(),
        },
    )
