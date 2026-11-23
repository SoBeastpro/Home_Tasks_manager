"""Представления дел: данные загружаются через Django ORM."""

from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from chores.forms import ChoreFilterForm, ChoreForm
from chores.models import Chore


SORT_FIELDS = {
    "date": "due_date",
    "title": "title",
    "user": "user__name",
    "category": "category__name",
    "priority": "-priority",
}
PAGE_SIZE = 5
CATEGORY_BUSY_MESSAGE = (
    "В этой категории на выбранную дату уже есть невыполненное дело."
)


def _parse_date(value: str):
    """Преобразовать строку YYYY-MM-DD в дату или вернуть None."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _chore_queryset():
    """Вернуть дела вместе с исполнителем и категорией."""
    return Chore.objects.select_related("user", "category")


def _category_slot_taken(form: ChoreForm) -> bool:
    """Проверить, занята ли категория на выбранную дату."""
    category = form.cleaned_data["category"]
    due_date = form.cleaned_data["due_date"]
    occupied = Chore.objects.occupying(category, due_date)
    if form.instance.pk:
        occupied = occupied.exclude(pk=form.instance.pk)
    return occupied.exists()


def chore_list(request: HttpRequest) -> HttpResponse:
    """Показать список дел с поиском, фильтрами и пагинацией."""
    form = ChoreFilterForm(request.GET or None)
    form_valid = form.is_bound and form.is_valid()
    error = None
    query = ""
    due_date = None
    category_id = None
    user_id = None
    sort = "date"

    if form.is_bound:
        if form_valid:
            query = (form.cleaned_data.get("q") or "").strip()
            due_date = form.cleaned_data.get("date")
            category = form.cleaned_data.get("category")
            user = form.cleaned_data.get("user")
            category_id = category.pk if category else None
            user_id = user.pk if user else None
            sort = form.cleaned_data.get("sort") or "date"
        else:
            error = "Проверьте корректность параметров фильтрации."

    chores = _chore_queryset()
    if form_valid:
        if query:
            chores = chores.filter(
                Q(title__icontains=query)
                | Q(user__name__icontains=query),
            )
        if due_date:
            chores = chores.filter(due_date=due_date)
        if category_id:
            chores = chores.filter(category_id=category_id)
        if user_id:
            chores = chores.filter(user_id=user_id)

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
            "form": form,
            "query": query,
            "due_date": due_date,
            "selected_category": category_id,
            "selected_user": user_id,
            "sort": sort,
            "error": error,
        },
    )


def open_chores(request: HttpRequest) -> HttpResponse:
    """Показать невыполненные дела."""
    chores = _chore_queryset().open().order_by("due_date", "pk")
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
                .for_date(selected_date)
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


def chore_create(request: HttpRequest) -> HttpResponse:
    """Создать новое домашнее дело."""
    if request.method == "POST":
        form = ChoreForm(request.POST)
        if form.is_valid():
            if _category_slot_taken(form):
                form.add_error(None, CATEGORY_BUSY_MESSAGE)
            else:
                form.save()
                return redirect("chores:list")
    else:
        form = ChoreForm(
            initial={"due_date": timezone.localdate()},
        )
    return render(
        request,
        "chores/chore_form.html",
        {
            "form": form,
            "title": "Новое дело",
        },
    )


def chore_update(request: HttpRequest, chore_id: int) -> HttpResponse:
    """Изменить существующее невыполненное дело."""
    chore = get_object_or_404(
        _chore_queryset().open(),
        pk=chore_id,
    )
    if request.method == "POST":
        form = ChoreForm(request.POST, instance=chore)
        if form.is_valid():
            if _category_slot_taken(form):
                form.add_error(None, CATEGORY_BUSY_MESSAGE)
            else:
                form.save()
                return redirect(chore)
    else:
        form = ChoreForm(instance=chore)
    return render(
        request,
        "chores/chore_form.html",
        {
            "form": form,
            "chore": chore,
            "title": "Изменить дело",
        },
    )


@require_POST
def chore_complete(request: HttpRequest, chore_id: int) -> HttpResponse:
    """Отметить невыполненное дело выполненным."""
    chore = get_object_or_404(
        _chore_queryset().open(),
        pk=chore_id,
    )
    chore.complete()
    return redirect("chores:list")
