"""Представления списка и карточки домашних дел."""

from datetime import date
from html import escape

from django.http import HttpRequest, HttpResponse

from homepage.views import page
from models.chores import find_chore_by_id
from storage import load_categories, load_chores, load_users
from utils import format_date


def _load_chores():
    """Загрузить объекты Chore из JSON через storage."""
    users = load_users()
    categories = load_categories()
    return load_chores(users, categories)


def chore_list(request: HttpRequest) -> HttpResponse:
    """Показать список дел из JSON."""
    chores = _load_chores()
    if not chores:
        content = "<p>Дела ещё не добавлены.</p>"
    else:
        rows = []
        for chore in chores:
            title = escape(chore.title)
            user_name = escape(chore.user.name)
            category_name = escape(chore.category.name)
            status_name = escape(str(chore.status))
            due = format_date(chore.due_date)
            rows.append(
                "<tr>"
                f"<td>{chore.id}</td>"
                f'<td><a href="/chores/{chore.id}/">{title}</a></td>'
                f"<td>{user_name}</td>"
                f"<td>{category_name}</td>"
                f"<td>{due}</td>"
                f"<td>{status_name}</td>"
                "</tr>"
            )
        content = (
            '<table class="table table-striped table-hover">'
            "<thead><tr>"
            "<th>№</th><th>Название</th><th>Исполнитель</th>"
            "<th>Категория</th><th>Срок</th><th>Статус</th>"
            "</tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>"
        )
    return HttpResponse(page("Дела", content, active="chores"))


def chore_detail(request: HttpRequest, chore_id: int) -> HttpResponse:
    """Показать карточку дела или страницу 404."""
    chore = find_chore_by_id(_load_chores(), chore_id)
    if chore is None:
        content = (
            f"<p>Дело с номером {chore_id} не найдено.</p>"
            '<p><a class="btn btn-success" href="/chores/">'
            "К списку дел</a></p>"
        )
        return HttpResponse(
            page("Дело не найдено", content, active="chores"),
            status=404,
        )
    hint = escape(chore.deadline_message(date.today()))
    content = f"""
    <div class="card">
      <div class="card-body">
        <p><strong>Исполнитель:</strong> {escape(chore.user.name)}</p>
        <p><strong>Категория:</strong>
           <a href="/categories/{chore.category.id}/">
           {escape(chore.category.name)}</a></p>
        <p><strong>Срок:</strong> {format_date(chore.due_date)}</p>
        <p><strong>Статус:</strong> {escape(str(chore.status))}</p>
        <p><strong>Приоритет:</strong> {escape(chore.priority_label)}</p>
        <p><strong>Подсказка:</strong> {hint}</p>
        <a class="btn btn-outline-success" href="/chores/">
          К списку дел
        </a>
      </div>
    </div>
    """
    title = f"Дело №{chore.id}: {chore.title}"
    return HttpResponse(page(title, content, active="chores"))
