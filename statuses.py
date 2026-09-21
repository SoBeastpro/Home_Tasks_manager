"""Сущность «Статус» домашнего дела.

Перечень статусов хранится в кортеже, потому что порядок статусов
в жизненном цикле дела фиксирован и не должен изменяться.
Для быстрой проверки принадлежности статуса используется множество.
"""

STATUS_PLANNED = "Запланировано"
STATUS_IN_PROGRESS = "В работе"
STATUS_DONE = "Выполнено"

STATUSES: tuple[str, ...] = (
    STATUS_PLANNED,
    STATUS_IN_PROGRESS,
    STATUS_DONE,
)

KNOWN_STATUSES: frozenset[str] = frozenset(STATUSES)


def is_valid_status(status: str) -> bool:
    """Проверить, входит ли статус в перечень допустимых."""
    return status.strip() in KNOWN_STATUSES


def normalize_status(status: str) -> str:
    """Привести статус к каноническому написанию.

    Регистр символов при вводе не учитывается.
    Вызывает ValueError, если статус не входит в перечень допустимых.
    """
    value = status.strip()
    for known_status in STATUSES:
        if value.lower() == known_status.lower():
            return known_status
    raise ValueError(f"Недопустимый статус: «{status}»")


def status_by_number(number: int) -> str:
    """Вернуть статус по его порядковому номеру в меню (нумерация с 1)."""
    if number < 1 or number > len(STATUSES):
        raise ValueError(f"Статуса с номером {number} не существует")
    return STATUSES[number - 1]


def next_status(status: str) -> str:
    """Вернуть следующий статус в жизненном цикле дела.

    Для завершающего статуса возвращается он же.
    """
    current_status = normalize_status(status)
    position = STATUSES.index(current_status)
    if position == len(STATUSES) - 1:
        return current_status
    return STATUSES[position + 1]
