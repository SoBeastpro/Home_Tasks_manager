"""Класс Chore и функции работы с коллекцией домашних дел.

Дело связывает пользователя и категорию: в объекте хранятся ссылки
на объекты User и Category, а не только их идентификаторы.
Функции get_chore_status(), get_days_left(), get_deadline_message()
и get_priority_label() сохранены из ПР1 и используются вместе
с методами объекта Chore.
"""

from collections.abc import Iterator
from datetime import date

from utils import date_to_storage, format_date, parse_date

from .categories import Category
from .statuses import STATUS_DONE, STATUSES, PlannedStatus, Status
from .users import User

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


class Chore:
    """Домашнее дело, закреплённое за пользователем и категорией."""

    def __init__(
        self,
        chore_id: int,
        title: str,
        user: User,
        category: Category,
        due_date: str | date,
        priority: int = 2,
        status: Status | str | None = None,
    ) -> None:
        """Создать объект домашнего дела."""
        self.id = chore_id
        self.title = self.validate_title(title)
        self.user = user
        self.category = category
        self.priority = self.validate_priority(priority)
        self.due_date = date_to_storage(due_date)
        if status is None:
            self._status: Status = PlannedStatus()
        elif isinstance(status, Status):
            self._status = status
        else:
            self._status = Status.from_name(status)

    @property
    def status(self) -> Status:
        """Вернуть текущий объект статуса дела."""
        return self._status

    @property
    def priority_label(self) -> str:
        """Вернуть название приоритета дела."""
        return PRIORITY_LABELS[self.priority]

    @staticmethod
    def validate_title(title: str) -> str:
        """Проверить название дела и вернуть его без пробелов по краям."""
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Название дела не может быть пустым")
        return clean_title

    @staticmethod
    def validate_priority(priority: int | str) -> int:
        """Проверить приоритет дела и вернуть его числовой уровень."""
        level = int(priority)
        if level not in PRIORITY_LABELS:
            raise ValueError(f"Недопустимый приоритет: {priority}")
        return level

    def is_done(self) -> bool:
        """Проверить, выполнено ли дело."""
        return self._status.is_done()

    def set_status(self, status: Status | str) -> None:
        """Изменить статус дела."""
        if isinstance(status, Status):
            self._status = status
        else:
            self._status = Status.from_name(status)

    def complete(self) -> None:
        """Отметить дело выполненным."""
        self.set_status(STATUS_DONE)

    def days_left(self, today: date) -> int:
        """Вернуть количество дней до срока выполнения."""
        return get_days_left(self.due_date, today)

    def deadline_message(self, today: date) -> str:
        """Вернуть подсказку о сроке выполнения дела."""
        return get_deadline_message(self.days_left(today), self.is_done())

    def is_overdue(self, today: date) -> bool:
        """Проверить, просрочено ли невыполненное дело."""
        return not self.is_done() and parse_date(self.due_date) < today

    def is_on_date(self, day: str | date) -> bool:
        """Проверить, запланировано ли дело на указанную дату."""
        return parse_date(self.due_date) == parse_date(day)

    def matches(self, query: str) -> bool:
        """Проверить, встречается ли подстрока в названии дела."""
        return query.strip().lower() in self.title.lower()

    def to_data(self) -> dict:
        """Вернуть данные дела для сохранения в JSON."""
        return {
            "id": self.id,
            "title": self.title,
            "user_id": self.user.id,
            "category_id": self.category.id,
            "priority": self.priority,
            "due_date": self.due_date,
            "status": self.status.name,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление дела."""
        return (
            f"Дело №{self.id}: {self.title} "
            f"({self.category.name}, {self.user.name}, "
            f"{self.status}, до {format_date(self.due_date)})"
        )


def get_next_chore_id(chores: list[Chore]) -> int:
    """Вернуть свободный идентификатор для нового дела."""
    if not chores:
        return 1
    return max(chore.id for chore in chores) + 1


def add_chore(
    chores: list[Chore],
    title: str,
    user: User,
    category: Category,
    due_date: str | date,
    priority: int = 2,
) -> Chore:
    """Создать объект Chore, добавить его в коллекцию и вернуть."""
    chore = Chore(
        get_next_chore_id(chores),
        title,
        user,
        category,
        due_date,
        priority,
    )
    chores.append(chore)
    return chore


def find_chore(chores: list[Chore], chore_id: int) -> Chore:
    """Найти дело по идентификатору.

    Вызывает KeyError, если дело не найдено.
    """
    for chore in chores:
        if chore.id == chore_id:
            return chore
    raise KeyError(f"Дело с номером {chore_id} не найдено")


def search_chores(chores: list[Chore], query: str) -> list[Chore]:
    """Найти дела по подстроке названия."""
    return [chore for chore in chores if chore.matches(query)]


def iter_chores_by_user(
    chores: list[Chore],
    user_id: int,
) -> Iterator[Chore]:
    """Последовательно вернуть дела выбранного пользователя."""
    for chore in chores:
        if chore.user.id == user_id:
            yield chore


def filter_chores_by_user(chores: list[Chore], user_id: int) -> list[Chore]:
    """Отобрать дела выбранного пользователя."""
    return list(iter_chores_by_user(chores, user_id))


def filter_chores_by_category(
    chores: list[Chore],
    category_id: int,
) -> list[Chore]:
    """Отобрать дела выбранной категории."""
    return [
        chore for chore in chores if chore.category.id == category_id
    ]


def filter_chores_by_status(
    chores: list[Chore],
    status: Status | str,
) -> list[Chore]:
    """Отобрать дела с указанным статусом."""
    wanted = status if isinstance(status, Status) else Status.from_name(status)
    return [chore for chore in chores if chore.status == wanted]


def sort_chores(chores: list[Chore], key: str = "due_date") -> list[Chore]:
    """Вернуть дела, упорядоченные по сроку, приоритету или названию."""
    if key not in SORT_KEYS:
        raise ValueError(f"Неизвестный способ сортировки: {key}")
    if key == "priority":
        return sorted(
            chores,
            key=lambda chore: (-chore.priority, chore.due_date),
        )
    if key == "title":
        return sorted(chores, key=lambda chore: chore.title.lower())
    return sorted(
        chores,
        key=lambda chore: (chore.due_date, -chore.priority),
    )


def set_chore_status(
    chores: list[Chore],
    chore_id: int,
    status: Status | str,
) -> Chore:
    """Найти дело и изменить его статус через метод объекта."""
    chore = find_chore(chores, chore_id)
    chore.set_status(status)
    return chore


def complete_chore(chores: list[Chore], chore_id: int) -> Chore:
    """Найти дело и отметить его выполненным."""
    chore = find_chore(chores, chore_id)
    chore.complete()
    return chore


def delete_chore(chores: list[Chore], chore_id: int) -> Chore:
    """Удалить дело из списка и вернуть удалённый объект."""
    chore = find_chore(chores, chore_id)
    chores.remove(chore)
    return chore


def is_chore_done(chore: Chore) -> bool:
    """Проверить, выполнено ли дело."""
    return chore.is_done()


def get_chores_for_date(
    chores: list[Chore],
    day: str | date,
) -> list[Chore]:
    """Отобрать дела, запланированные на указанную дату."""
    return [chore for chore in chores if chore.is_on_date(day)]


def get_overdue_chores(chores: list[Chore], today: date) -> list[Chore]:
    """Отобрать невыполненные дела, срок которых уже прошёл."""
    return [chore for chore in chores if chore.is_overdue(today)]


def count_chores_by_status(chores: list[Chore]) -> dict[str, int]:
    """Посчитать количество дел по каждому статусу."""
    counters = {status: 0 for status in STATUSES}
    for chore in chores:
        counters[chore.status.name] = counters.get(chore.status.name, 0) + 1
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
    return PRIORITY_LABELS[Chore.validate_priority(priority)]


def show_chores(chores: list[Chore], title: str = "Список дел") -> None:
    """Вывести информацию об объектах Chore."""
    print(f"\n{title} ({len(chores)}):")
    if not chores:
        print("Дел не найдено.")
        return
    for chore in sort_chores(chores):
        print(f"  {chore}")
