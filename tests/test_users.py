"""Автоматические тесты функций работы с пользователями."""

from datetime import date

import pytest

from chores import add_chore, complete_chore
from users import (
    add_user,
    get_user,
    get_user_name,
    get_user_workload,
    search_users,
    sort_users,
)


def make_users() -> dict[int, dict]:
    """Подготовить словарь пользователей для тестов."""
    users: dict[int, dict] = {}
    add_user(users, "Алексей")
    add_user(users, "Мария")
    return users


def test_add_user():
    """Пользователь добавляется в словарь и получает идентификатор."""
    users = make_users()
    assert len(users) == 2
    assert users[1]["name"] == "Алексей"


def test_add_duplicate_user():
    """Повторное имя пользователя приводит к ValueError."""
    users = make_users()
    with pytest.raises(ValueError):
        add_user(users, "мария")


def test_search_users():
    """Поиск находит пользователя по части имени."""
    found = search_users(make_users(), "мар")
    assert len(found) == 1
    assert found[0]["name"] == "Мария"


def test_sort_users():
    """Пользователи упорядочиваются по имени."""
    users = make_users()
    add_user(users, "Борис")
    names = [user["name"] for user in sort_users(users)]
    assert names == ["Алексей", "Борис", "Мария"]


def test_get_missing_user():
    """Обращение к несуществующему пользователю приводит к KeyError."""
    with pytest.raises(KeyError):
        get_user(make_users(), 99)


def test_get_user_name_for_missing_user():
    """Для неизвестного исполнителя возвращается понятная пометка."""
    assert get_user_name(make_users(), 99) == "не назначен"


def test_get_user_workload():
    """Нагрузка считает только невыполненные дела пользователя."""
    users = make_users()
    chores: list[dict] = []
    add_chore(chores, "Помыть посуду", 1, 1, date(2026, 9, 25))
    add_chore(chores, "Вынести мусор", 1, 2, date(2026, 9, 26))
    add_chore(chores, "Купить продукты", 2, 3, date(2026, 9, 27))
    complete_chore(chores, 2)
    workload = get_user_workload(users, chores)
    assert workload == {"Алексей": 1, "Мария": 1}
