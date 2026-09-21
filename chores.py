"""Сущность «Дело»: домашние задачи и операции над ними.

Дела хранятся в списке словарей: порядок записей важен, а состав
списка постоянно изменяется. Функции get_chore_status(),
get_days_left(), get_deadline_message() и get_priority_label()
перенесены из начального сценария ПР1 и используются вместе
с новыми функциями модуля.
"""

from collections.abc import Iterator
from datetime import date

from statuses import STATUS_DONE, STATUS_PLANNED, STATUSES, normalize_status
from utils import date_to_storage, parse_date

PRIORITY_LABELS: dict[int, str] = {
    1: "Низкий",
    2: "Обычный",
    3: "Высокий",
}

SORT_KEYS: dict[str, str] = {
    "due_date": "по сроку выполнения",
    "priority": "по приоритету",
    "title": "по названию",
}


def get_next_chore_id(chores: list[dict]) -> int:
    """Вернуть свободный идентификатор для нового дела."""
    if not chores:
        return 1
    return max(chore["id"] for chore in chores) + 1


def add_chore(
    chores: list[dict],
    title: str,
    user_id: int,
    category_id: int,
    due_date: str | date,
    priority: int = 2,
) -> dict:
    """Добавить новое дело в список chores и вернуть его.

    Вызывает ValueError при пустом названии, недопустимом приоритете
    или некорректной дате.
    """
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("Название дела не может быть пустым")
    priority_level = int(priority)
    if priority_level not in PRIORITY_LABELS:
        raise ValueError(f"Недопустимый приоритет: {priority}")
    chore = {
        "id": get_next_chore_id(chores),
        "title": clean_title,
        "user_id": int(user_id),
        "category_id": int(category_id),
        "priority": priority_level,
        "due_date": date_to_storage(due_date),
        "status": STATUS_PLANNED,
    }
    chores.append(chore)
    return chore


def find_chore(chores: list[dict], chore_id: int) -> dict:
    """Найти дело по идентификатору.

    Вызывает KeyError, если дело не найдено.
    """
    for chore in chores:
        if chore["id"] == chore_id:
            return chore
    raise KeyError(f"Дело с номером {chore_id} не найдено")


def search_chores(chores: list[dict], query: str) -> list[dict]:
    """Найти дела по подстроке названия."""
    text = query.strip().lower()
    return [chore for chore in chores if text in chore["title"].lower()]


def iter_chores_by_user(
    chores: list[dict],
    user_id: int,
) -> Iterator[dict]:
    """Последовательно вернуть дела выбранного пользователя."""
    for chore in chores:
        if chore["user_id"] == user_id:
            yield chore


def filter_chores_by_user(chores: list[dict], user_id: int) -> list[dict]:
    """Отобрать дела выбранного пользователя."""
    return list(iter_chores_by_user(chores, user_id))


def filter_chores_by_category(
    chores: list[dict],
    category_id: int,
) -> list[dict]:
    """Отобрать дела выбранной категории."""
    return [chore for chore in chores if chore["category_id"] == category_id]


def filter_chores_by_status(chores: list[dict], status: str) -> list[dict]:
    """Отобрать дела с указанным статусом."""
    wanted_status = normalize_status(status)
    return [chore for chore in chores if chore["status"] == wanted_status]


def sort_chores(chores: list[dict], key: str = "due_date") -> list[dict]:
    """Вернуть дела, упорядоченные по сроку, приоритету или названию.

    Вызывает ValueError, если способ сортировки не поддерживается.
    """
    if key not in SORT_KEYS:
        raise ValueError(f"Неизвестный способ сортировки: {key}")
    if key == "priority":
        return sorted(
            chores,
            key=lambda chore: (-chore["priority"], chore["due_date"]),
        )
    if key == "title":
        return sorted(chores, key=lambda chore: chore["title"].lower())
    return sorted(
        chores,
        key=lambda chore: (chore["due_date"], -chore["priority"]),
    )


def set_chore_status(
    chores: list[dict],
    chore_id: int,
    status: str,
) -> dict:
    """Изменить статус дела и вернуть обновленное дело."""
    chore = find_chore(chores, chore_id)
    chore["status"] = normalize_status(status)
    return chore


def complete_chore(chores: list[dict], chore_id: int) -> dict:
    """Отметить дело выполненным."""
    return set_chore_status(chores, chore_id, STATUS_DONE)


def delete_chore(chores: list[dict], chore_id: int) -> dict:
    """Удалить дело из списка и вернуть удаленную запись."""
    chore = find_chore(chores, chore_id)
    chores.remove(chore)
    return chore


def is_chore_done(chore: dict) -> bool:
    """Проверить, выполнено ли дело."""
    return chore["status"] == STATUS_DONE


def get_chores_for_date(chores: list[dict], day: str | date) -> list[dict]:
    """Отобрать дела, запланированные на указанную дату."""
    wanted_day = parse_date(day)
    return [
        chore
        for chore in chores
        if parse_date(chore["due_date"]) == wanted_day
    ]


def get_overdue_chores(chores: list[dict], today: date) -> list[dict]:
    """Отобрать невыполненные дела, срок которых уже прошел."""
    return [
        chore
        for chore in chores
        if not is_chore_done(chore) and parse_date(chore["due_date"]) < today
    ]


def count_chores_by_status(chores: list[dict]) -> dict[str, int]:
    """Посчитать количество дел по каждому статусу."""
    counters = {status: 0 for status in STATUSES}
    for chore in chores:
        counters[chore["status"]] = counters.get(chore["status"], 0) + 1
    return counters


def get_chore_status(is_done: bool) -> str:
    """Вернуть текстовую отметку о выполнении дела (функция из ПР1)."""
    if is_done:
        return "Выполнено"
    return "Не выполнено"


def get_days_left(due_date: str | date, today: date) -> int:
    """Вернуть количество дней до срока выполнения дела (функция из ПР1)."""
    return (parse_date(due_date) - today).days


def get_deadline_message(days_left: int, is_done: bool) -> str:
    """Вернуть подсказку о сроке выполнения дела (функция из ПР1)."""
    if is_done:
        return "Дело выполнено, срок уже не важен"
    if days_left < 0:
        return f"Срок пропущен {-days_left} дн. назад"
    elif days_left == 0:
        return "Сделать сегодня"
    elif days_left <= 2:
        return "Срок скоро истекает"
    return "Времени достаточно"


def get_priority_label(priority: int | str) -> str:
    """Вернуть название приоритета дела по его уровню (функция из ПР1)."""
    level = int(priority)
    if level not in PRIORITY_LABELS:
        raise ValueError(f"Недопустимый приоритет: {priority}")
    return PRIORITY_LABELS[level]
