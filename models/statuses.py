"""Сущность «Статус» домашнего дела.

Базовый класс Status описывает общее поведение статуса.
Конкретные состояния реализованы наследниками: у каждого своё
имя, признак завершения и правило перехода к следующему статусу.
Это отношение «является»: PlannedStatus является статусом.
"""

STATUS_PLANNED = "Запланировано"
STATUS_IN_PROGRESS = "В работе"
STATUS_DONE = "Выполнено"

STATUSES: tuple[str, ...] = (
    STATUS_PLANNED,
    STATUS_IN_PROGRESS,
    STATUS_DONE,
)


class Status:
    """Базовый статус домашнего дела."""

    name = ""

    def is_done(self) -> bool:
        """Проверить, означает ли статус завершение дела."""
        return False

    def next_status(self) -> "Status":
        """Вернуть следующий статус в жизненном цикле дела."""
        return self

    def __eq__(self, other: object) -> bool:
        """Сравнить статусы по названию, в том числе со строкой."""
        if isinstance(other, Status):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return NotImplemented

    def __str__(self) -> str:
        """Вернуть название статуса."""
        return self.name

    @classmethod
    def from_name(cls, name: str) -> "Status":
        """Создать объект статуса по текстовому названию.

        Регистр символов при поиске не учитывается.
        Вызывает ValueError, если статус не входит в перечень.
        """
        value = name.strip().lower()
        for status_class in STATUS_CLASSES:
            if status_class.name.lower() == value:
                return status_class()
        raise ValueError(f"Недопустимый статус: «{name}»")


class PlannedStatus(Status):
    """Статус «Запланировано»: дело ещё не начато."""

    name = STATUS_PLANNED

    def next_status(self) -> Status:
        """Перевести дело в работу."""
        return InProgressStatus()


class InProgressStatus(Status):
    """Статус «В работе»: дело выполняется."""

    name = STATUS_IN_PROGRESS

    def next_status(self) -> Status:
        """Отметить дело выполненным."""
        return DoneStatus()


class DoneStatus(Status):
    """Статус «Выполнено»: работа по делу завершена."""

    name = STATUS_DONE

    def is_done(self) -> bool:
        """Выполненное дело больше не требует действий."""
        return True


STATUS_CLASSES: tuple[type[Status], ...] = (
    PlannedStatus,
    InProgressStatus,
    DoneStatus,
)


def is_valid_status(status: str) -> bool:
    """Проверить, входит ли статус в перечень допустимых."""
    try:
        Status.from_name(status)
    except ValueError:
        return False
    return True


def normalize_status(status: str) -> str:
    """Привести статус к каноническому написанию."""
    return Status.from_name(status).name


def status_by_number(number: int) -> Status:
    """Вернуть объект статуса по номеру пункта меню (с 1)."""
    if number < 1 or number > len(STATUS_CLASSES):
        raise ValueError(f"Статуса с номером {number} не существует")
    return STATUS_CLASSES[number - 1]()


def next_status(status: str) -> str:
    """Вернуть название следующего статуса в жизненном цикле."""
    return Status.from_name(status).next_status().name
