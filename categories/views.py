"""Представления категорий: данные загружаются через Django ORM."""

from django.db.models import Avg, Count, Max, Min, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from categories.models import Category
from chores.models import Chore, Status


def category_list(request: HttpRequest) -> HttpResponse:
    """Показать список категорий и число дел в каждой."""
    categories = Category.objects.annotate(
        chore_count=Count("chores"),
    ).order_by("name")
    return render(
        request,
        "categories/category_list.html",
        {"categories": categories},
    )


def category_detail(
    request: HttpRequest,
    slug: str,
) -> HttpResponse:
    """Показать категорию и её дела или страницу 404."""
    category = get_object_or_404(Category, slug=slug)
    chores = (
        Chore.objects.select_related("user", "category")
        .filter(category=category)
        .order_by("due_date", "pk")
    )
    return render(
        request,
        "categories/category_detail.html",
        {
            "category": category,
            "chores": chores,
        },
    )


def statistics(request: HttpRequest) -> HttpResponse:
    """Показать статистику дел по категориям и статусам."""
    by_category = (
        Category.objects.annotate(
            chores_count=Count("chores"),
        )
        .values("name", "chores_count")
        .order_by("-chores_count")
    )
    by_status = (
        Chore.objects.values("status")
        .annotate(chores_count=Count("id"))
        .order_by("-chores_count")
    )
    busy_categories = by_category.filter(chores_count__gt=1)
    summary = Chore.objects.aggregate(
        chores_count=Count("id"),
        open_count=Count("id", filter=~Q(status=Status.DONE)),
        avg_priority=Avg("priority"),
        min_priority=Min("priority"),
        max_priority=Max("priority"),
    )
    return render(
        request,
        "categories/statistics.html",
        {
            "by_category": [
                {
                    "category_name": item["name"],
                    "chores_count": item["chores_count"],
                }
                for item in by_category
            ],
            "by_status": by_status,
            "busy_categories": [
                {
                    "category_name": item["name"],
                    "chores_count": item["chores_count"],
                }
                for item in busy_categories
            ],
            "open_count": summary["open_count"],
            "summary": summary,
        },
    )
