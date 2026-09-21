"""Автоматические тесты функций работы с домашними делами."""

from datetime import date

import pytest

from chores import (
    add_chore,
    complete_chore,
    count_chores_by_status,
    delete_chore,
    filter_chores_by_status,
    filter_chores_by_user,
    find_chore,
    get_days_left,
    get_deadline_message,
    get_overdue_chores,
    is_chore_done,
    search_chores,
    set_chore_status,
    sort_chores,
)
from statuses import STATUS_DONE, STATUS_PLANNED


def make_chores() -> list[dict]:
    """Подготовить набор дел для тестов."""
    chores: list[dict] = []
    add_chore(chores, "Помыть посуду", 1, 1, date(2026, 9, 18), 3)
    add_chore(chores, "Купить продукты", 2, 3, date(2026, 9, 25), 2)
    add_chore(chores, "Пропылесосить ковер", 1, 2, date(2026, 9, 30), 1)
    return chores


def test_add_chore():
    """Новое дело попадает в список со статусом «Запланировано»."""
    chores: list[dict] = []
    chore = add_chore(chores, "Помыть посуду", 1, 1, date(2026, 9, 25))
    assert len(chores) == 1
    assert chore["status"] == STATUS_PLANNED
    assert chore["due_date"] == "2026-09-25"


def test_add_chore_with_empty_title():
    """Дело без названия добавить нельзя."""
    with pytest.raises(ValueError):
        add_chore([], "   ", 1, 1, date(2026, 9, 25))


def test_search_chores():
    """Поиск находит дело по части названия без учета регистра."""
    found = search_chores(make_chores(), "ПОСУД")
    assert len(found) == 1
    assert found[0]["title"] == "Помыть посуду"


def test_filter_chores_by_user():
    """Отбор по исполнителю возвращает только его дела."""
    found = filter_chores_by_user(make_chores(), 1)
    assert len(found) == 2


def test_complete_chore():
    """Выполненное дело меняет статус и попадает в нужную выборку."""
    chores = make_chores()
    chore = complete_chore(chores, 1)
    assert is_chore_done(chore)
    assert filter_chores_by_status(chores, STATUS_DONE) == [chore]


def test_set_unknown_status():
    """Недопустимый статус приводит к ValueError."""
    with pytest.raises(ValueError):
        set_chore_status(make_chores(), 1, "Отложено")


def test_find_missing_chore():
    """Поиск несуществующего дела приводит к KeyError."""
    with pytest.raises(KeyError):
        find_chore(make_chores(), 99)


def test_delete_chore():
    """Удаленное дело исчезает из списка."""
    chores = make_chores()
    deleted = delete_chore(chores, 2)
    assert deleted["title"] == "Купить продукты"
    assert len(chores) == 2


def test_sort_chores_by_priority():
    """Сортировка по приоритету ставит срочные дела первыми."""
    chores = sort_chores(make_chores(), "priority")
    assert chores[0]["title"] == "Помыть посуду"
    assert chores[-1]["title"] == "Пропылесосить ковер"


def test_get_overdue_chores():
    """Просроченными считаются невыполненные дела с прошедшим сроком."""
    overdue = get_overdue_chores(make_chores(), date(2026, 9, 21))
    assert len(overdue) == 1
    assert overdue[0]["title"] == "Помыть посуду"


def test_count_chores_by_status():
    """Статистика учитывает все статусы дел."""
    chores = make_chores()
    complete_chore(chores, 1)
    counters = count_chores_by_status(chores)
    assert counters[STATUS_DONE] == 1
    assert counters[STATUS_PLANNED] == 2


def test_get_days_left():
    """Количество дней до срока считается по датам."""
    assert get_days_left("2026-09-25", date(2026, 9, 21)) == 4


def test_get_deadline_message():
    """Подсказка о сроке зависит от количества оставшихся дней."""
    assert get_deadline_message(-2, False) == "Срок пропущен 2 дн. назад"
    assert get_deadline_message(0, False) == "Сделать сегодня"
    assert get_deadline_message(10, False) == "Времени достаточно"
