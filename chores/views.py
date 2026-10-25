"""Представления дел: данные загружаются из SQLite."""

from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from models.chores import get_deadline_message
from utils import parse_date


CHORES_LIST_SQL = """
SELECT
    chores.id,
    chores.category_id,
    chores.title,
    chores.due_date,
    chores.status,
    chores.priority,
    CASE chores.priority
        WHEN 1 THEN 'Низкий'
        WHEN 2 THEN 'Обычный'
        WHEN 3 THEN 'Высокий'
    END AS priority_label,
    users.name AS user_name,
    categories.name AS category_name
FROM chores
JOIN users
    ON chores.user_id = users.id
JOIN categories
    ON chores.category_id = categories.id
"""


def chore_list(request: HttpRequest) -> HttpResponse:
    """Показать список дел из SQLite."""
    conn = get_connection()
    chores = conn.execute(
        CHORES_LIST_SQL + "ORDER BY chores.due_date;",
    ).fetchall()
    conn.close()
    return render(request, "chores/chore_list.html", {"chores": chores})


def open_chores(request: HttpRequest) -> HttpResponse:
    """Показать невыполненные дела."""
    conn = get_connection()
    chores = conn.execute(
        CHORES_LIST_SQL
        + "WHERE chores.status != ? "
        + "ORDER BY chores.due_date;",
        ("Выполнено",),
    ).fetchall()
    conn.close()
    return render(
        request,
        "chores/open_list.html",
        {"chores": chores},
    )


def chores_by_date(request: HttpRequest) -> HttpResponse:
    """Найти дела на выбранную дату."""
    due_date = request.GET.get("date")
    chores = []
    if due_date:
        conn = get_connection()
        chores = conn.execute(
            CHORES_LIST_SQL
            + "WHERE chores.due_date = ? "
            + "ORDER BY chores.priority DESC;",
            (due_date,),
        ).fetchall()
        conn.close()
    return render(
        request,
        "chores/by_date.html",
        {
            "chores": chores,
            "due_date": due_date,
        },
    )


def chore_detail(request: HttpRequest, chore_id: int) -> HttpResponse:
    """Показать карточку дела или страницу 404."""
    conn = get_connection()
    chore = conn.execute(
        CHORES_LIST_SQL + "WHERE chores.id = ?;",
        (chore_id,),
    ).fetchone()
    conn.close()
    hint = ""
    if chore is not None:
        is_done = chore["status"] == "Выполнено"
        days_left = (parse_date(chore["due_date"]) - date.today()).days
        hint = get_deadline_message(days_left, is_done)
    return render(
        request,
        "chores/chore_detail.html",
        {
            "chore": chore,
            "deadline_hint": hint,
        },
        status=404 if chore is None else 200,
    )
