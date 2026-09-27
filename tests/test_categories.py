"""Автоматические тесты класса Category и функций работы с категориями."""

from datetime import date

import pytest

from models import Category, User
from models.categories import (
    add_category,
    count_chores_by_category,
    get_category_name,
    search_categories,
)
from models.chores import add_chore


def make_categories() -> list[Category]:
    """Подготовить коллекцию категорий для тестов."""
    categories: list[Category] = []
    add_category(categories, "Кухня")
    add_category(categories, "Уборка")
    return categories


def test_category_creation():
    """Объект Category сохраняет идентификатор и название."""
    category = Category(1, "Кухня")
    assert category.id == 1
    assert category.name == "Кухня"
    assert "Кухня" in str(category)


def test_category_from_data():
    """Метод from_data создаёт категорию из словаря."""
    category = Category.from_data({"id": 2, "name": "Уборка"})
    assert category.id == 2
    assert category.name == "Уборка"


def test_add_category():
    """Категория добавляется в коллекцию и получает идентификатор."""
    categories = make_categories()
    assert len(categories) == 2
    assert categories[1].name == "Уборка"
    assert isinstance(categories[1], Category)


def test_add_duplicate_category():
    """Повторное название категории приводит к ValueError."""
    categories = make_categories()
    with pytest.raises(ValueError):
        add_category(categories, "кухня")


def test_search_categories():
    """Поиск находит категорию по части названия."""
    found = search_categories(make_categories(), "убор")
    assert len(found) == 1
    assert found[0].name == "Уборка"


def test_get_category_name_for_missing_category():
    """Для неизвестной категории возвращается понятная пометка."""
    assert get_category_name(make_categories(), 99) == "без категории"


def test_count_chores_by_category():
    """Подсчёт дел выполняется по связанному объекту Category."""
    categories = make_categories()
    user = User(1, "Алексей")
    chores = []
    add_chore(chores, "Помыть посуду", user, categories[0], date(2026, 9, 25))
    add_chore(chores, "Протереть пыль", user, categories[1], date(2026, 9, 26))
    add_chore(chores, "Вынести мусор", user, categories[1], date(2026, 9, 27))
    assert count_chores_by_category(categories, chores) == {
        "Кухня": 1,
        "Уборка": 2,
    }
