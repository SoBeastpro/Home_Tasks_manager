"""Представления категорий: данные загружаются из SQLite."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from chores.views import CHORES_LIST_SQL


def category_list(request: HttpRequest) -> HttpResponse:
    """Показать список категорий из SQLite."""
    conn = get_connection()
    categories = conn.execute(
        """
        SELECT
            categories.id,
            categories.name,
            COUNT(chores.id) AS chore_count
        FROM categories
        LEFT JOIN chores
            ON categories.id = chores.category_id
        GROUP BY categories.id, categories.name
        ORDER BY categories.name;
        """
    ).fetchall()
    conn.close()
    return render(
        request,
        "categories/category_list.html",
        {"categories": categories},
    )


def category_detail(
    request: HttpRequest,
    category_id: int,
) -> HttpResponse:
    """Показать категорию и её дела или страницу 404."""
    conn = get_connection()
    category = conn.execute(
        """
        SELECT id, name
        FROM categories
        WHERE id = ?;
        """,
        (category_id,),
    ).fetchone()
    chores = []
    if category is not None:
        chores = conn.execute(
            CHORES_LIST_SQL + "WHERE chores.category_id = ? "
            + "ORDER BY chores.due_date;",
            (category_id,),
        ).fetchall()
    conn.close()
    return render(
        request,
        "categories/category_detail.html",
        {
            "category": category,
            "chores": chores,
        },
        status=404 if category is None else 200,
    )


def statistics(request: HttpRequest) -> HttpResponse:
    """Показать статистику дел по категориям и статусам."""
    conn = get_connection()
    by_category = conn.execute(
        """
        SELECT
            categories.name AS category_name,
            COUNT(chores.id) AS chores_count
        FROM categories
        LEFT JOIN chores
            ON categories.id = chores.category_id
        GROUP BY categories.id, categories.name
        ORDER BY chores_count DESC;
        """
    ).fetchall()
    by_status = conn.execute(
        """
        SELECT
            status,
            COUNT(*) AS chores_count
        FROM chores
        GROUP BY status
        ORDER BY chores_count DESC;
        """
    ).fetchall()
    busy_categories = conn.execute(
        """
        SELECT
            categories.name AS category_name,
            COUNT(chores.id) AS chores_count
        FROM categories
        JOIN chores
            ON categories.id = chores.category_id
        GROUP BY categories.id, categories.name
        HAVING COUNT(chores.id) > 1
        ORDER BY chores_count DESC;
        """
    ).fetchall()
    totals = conn.execute(
        """
        SELECT
            COUNT(*) AS chores_count
        FROM chores
        WHERE status != ?;
        """,
        ("Выполнено",),
    ).fetchone()
    conn.close()
    return render(
        request,
        "categories/statistics.html",
        {
            "by_category": by_category,
            "by_status": by_status,
            "busy_categories": busy_categories,
            "open_count": totals["chores_count"],
        },
    )
