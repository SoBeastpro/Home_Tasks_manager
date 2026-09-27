"""Автоматические тесты класса User и функций работы с пользователями."""

from datetime import date

import pytest

from models import Category, User
from models.chores import add_chore, complete_chore
from models.users import (
    add_user,
    find_user,
    get_user,
    get_user_name,
    get_user_workload,
    search_users,
    sort_users,
)


def make_users() -> list[User]:
    """Подготовить коллекцию пользователей для тестов."""
    users: list[User] = []
    add_user(users, "Алексей", "alexey@home.local")
    add_user(users, "Мария", "maria@home.local")
    return users


def test_user_creation():
    """Объект User сохраняет идентификатор, имя и почту."""
    user = User(1, "Иван Петров", "ivan@example.com")
    assert user.id == 1
    assert user.name == "Иван Петров"
    assert user.email == "ivan@example.com"
    assert "Иван Петров" in str(user)


def test_user_from_data():
    """Метод from_data создаёт пользователя из словаря."""
    user = User.from_data({
        "id": 2,
        "name": "Мария",
        "email": "maria@home.local",
    })
    assert user.id == 2
    assert user.name == "Мария"
    assert user.email == "maria@home.local"


def test_add_user():
    """Пользователь добавляется в коллекцию и получает идентификатор."""
    users = make_users()
    assert len(users) == 2
    assert users[0].name == "Алексей"
    assert isinstance(users[0], User)


def test_add_duplicate_user():
    """Повторное имя пользователя приводит к ValueError."""
    users = make_users()
    with pytest.raises(ValueError):
        add_user(users, "мария")


def test_search_users():
    """Поиск находит пользователя по части имени."""
    found = search_users(make_users(), "мар")
    assert len(found) == 1
    assert found[0].name == "Мария"


def test_find_user_by_email():
    """Поиск работает и по адресу электронной почты."""
    found = find_user(make_users(), "alexey@")
    assert len(found) == 1
    assert found[0].name == "Алексей"


def test_sort_users():
    """Пользователи упорядочиваются по имени."""
    users = make_users()
    add_user(users, "Борис")
    names = [user.name for user in sort_users(users)]
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
    kitchen = Category(1, "Кухня")
    cleaning = Category(2, "Уборка")
    shopping = Category(3, "Покупки")
    chores = []
    add_chore(chores, "Помыть посуду", users[0], kitchen, date(2026, 9, 25))
    add_chore(chores, "Вынести мусор", users[0], cleaning, date(2026, 9, 26))
    add_chore(chores, "Купить продукты", users[1], shopping, date(2026, 9, 27))
    complete_chore(chores, 2)
    workload = get_user_workload(users, chores)
    assert workload == {"Алексей": 1, "Мария": 1}
