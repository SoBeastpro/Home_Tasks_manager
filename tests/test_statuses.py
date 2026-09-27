"""Автоматические тесты иерархии статусов."""

import pytest

from models.statuses import (
    STATUS_DONE,
    STATUS_IN_PROGRESS,
    STATUS_PLANNED,
    DoneStatus,
    InProgressStatus,
    PlannedStatus,
    Status,
    is_valid_status,
    next_status,
    normalize_status,
    status_by_number,
)


def test_normalize_status():
    """Статус приводится к каноническому написанию."""
    assert normalize_status("выполнено") == STATUS_DONE
    assert is_valid_status(STATUS_PLANNED)
    assert not is_valid_status("Отложено")


def test_next_status():
    """Статус переходит к следующему в жизненном цикле дела."""
    assert next_status(STATUS_PLANNED) == STATUS_IN_PROGRESS
    assert next_status(STATUS_DONE) == STATUS_DONE


def test_status_by_number():
    """Номер пункта меню соответствует объекту статуса."""
    assert status_by_number(1) == PlannedStatus()
    with pytest.raises(ValueError):
        status_by_number(99)


def test_status_polymorphism():
    """Наследники Status по-разному отвечают на is_done()."""
    statuses = [PlannedStatus(), InProgressStatus(), DoneStatus()]
    results = [status.is_done() for status in statuses]
    assert results == [False, False, True]
    assert [str(status) for status in statuses] == [
        STATUS_PLANNED,
        STATUS_IN_PROGRESS,
        STATUS_DONE,
    ]


def test_status_from_name():
    """Классовый метод создаёт нужный подкласс статуса."""
    status = Status.from_name("в работе")
    assert isinstance(status, InProgressStatus)
    assert status.next_status().is_done()
