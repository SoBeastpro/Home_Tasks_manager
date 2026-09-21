"""Автоматические тесты функций работы с категориями и статусами."""

from datetime import date

import pytest

from categories import (
    add_category,
    count_chores_by_category,
    get_category_name,
    search_categories,
)
from chores import add_chore
from statuses import (
    STATUS_DONE,
    STATUS_IN_PROGRESS,
    STATUS_PLANNED,
    is_valid_status,
    next_status,
    normalize_status,
    status_by_number,
)


def make_categories() -> dict[int, dict]:
    """Подготовить словарь категорий для тестов."""
    categories: dict[int, dict] = {}
    add_category(categories, "Кухня")
    add_category(categories, "Уборка")
    return categories


def test_add_category():
    """Категория добавляется в словарь и получает идентификатор."""
    categories = make_categories()
    assert len(categories) == 2
    assert categories[2]["name"] == "Уборка"


def test_add_duplicate_category():
    """Повторное название категории приводит к ValueError."""
    categories = make_categories()
    with pytest.raises(ValueError):
        add_category(categories, "кухня")


def test_search_categories():
    """Поиск находит категорию по части названия."""
    found = search_categories(make_categories(), "убор")
    assert len(found) == 1
    assert found[0]["name"] == "Уборка"


def test_get_category_name_for_missing_category():
    """Для неизвестной категории возвращается понятная пометка."""
    assert get_category_name(make_categories(), 99) == "без категории"


def test_count_chores_by_category():
    """Подсчет дел выполняется по каждой категории."""
    categories = make_categories()
    chores: list[dict] = []
    add_chore(chores, "Помыть посуду", 1, 1, date(2026, 9, 25))
    add_chore(chores, "Протереть пыль", 1, 2, date(2026, 9, 26))
    add_chore(chores, "Вынести мусор", 2, 2, date(2026, 9, 27))
    assert count_chores_by_category(categories, chores) == {
        "Кухня": 1,
        "Уборка": 2,
    }


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
    """Номер пункта меню соответствует статусу из перечня."""
    assert status_by_number(1) == STATUS_PLANNED
    with pytest.raises(ValueError):
        status_by_number(99)
