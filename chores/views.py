"""Представления списка и карточки домашних дел."""

from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.chores import find_chore_by_id
from storage import load_categories, load_chores, load_users


def _load_chores():
    """Загрузить объекты Chore из JSON через storage."""
    users = load_users()
    categories = load_categories()
    return load_chores(users, categories)


def chore_list(request: HttpRequest) -> HttpResponse:
    """Показать список дел из JSON."""
    context = {"chores": _load_chores()}
    return render(request, "chores/chore_list.html", context)


def chore_detail(request: HttpRequest, chore_id: int) -> HttpResponse:
    """Показать карточку дела или страницу 404."""
    chore = find_chore_by_id(_load_chores(), chore_id)
    hint = ""
    if chore is not None:
        hint = chore.deadline_message(date.today())
    context = {
        "chore": chore,
        "deadline_hint": hint,
    }
    return render(
        request,
        "chores/chore_detail.html",
        context,
        status=404 if chore is None else 200,
    )
