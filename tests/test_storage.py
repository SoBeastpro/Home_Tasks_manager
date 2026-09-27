"""Автоматические тесты сохранения и загрузки объектов проекта."""

import pytest

from models import Category, Chore, User
from storage import (
    StorageError,
    load_categories,
    load_chores,
    load_items,
    load_users,
    save_categories,
    save_chores,
    save_items,
    save_users,
)


def test_load_items_for_missing_file(tmp_path):
    """Отсутствующий файл данных считается пустым набором записей."""
    assert load_items(str(tmp_path / "chores.json")) == []


def test_save_and_load_items(tmp_path):
    """Записанные в файл данные читаются без изменений."""
    filename = str(tmp_path / "data" / "users.json")
    users = [{"id": 1, "name": "Алексей"}]
    save_items(filename, users)
    assert load_items(filename) == users


def test_load_broken_file(tmp_path):
    """Поврежденный JSON-файл приводит к StorageError."""
    broken_file = tmp_path / "chores.json"
    broken_file.write_text("{ это не json", encoding="utf-8")
    with pytest.raises(StorageError):
        load_items(str(broken_file))


def test_save_and_load_users(tmp_path):
    """Пользователи сохраняются как объекты и восстанавливаются из JSON."""
    filename = str(tmp_path / "users.json")
    users = [User(1, "Алексей", "alexey@home.local")]
    save_users(users, filename)
    loaded = load_users(filename)
    assert len(loaded) == 1
    assert loaded[0].name == "Алексей"
    assert loaded[0].email == "alexey@home.local"


def test_save_and_load_chores(tmp_path):
    """При загрузке дела восстанавливаются связи с User и Category."""
    users = [User(1, "Алексей")]
    categories = [Category(1, "Кухня")]
    chores = [
        Chore(1, "Помыть посуду", users[0], categories[0], "2026-09-25", 3),
    ]
    chores_file = str(tmp_path / "chores.json")
    save_chores(chores, chores_file)
    loaded = load_chores(users, categories, chores_file)
    assert len(loaded) == 1
    assert loaded[0].user is users[0]
    assert loaded[0].category is categories[0]
    assert loaded[0].title == "Помыть посуду"


def test_load_chore_without_user(tmp_path):
    """Дело без существующего пользователя не создаётся."""
    categories = [Category(1, "Кухня")]
    filename = str(tmp_path / "chores.json")
    save_items(
        filename,
        [{
            "id": 1,
            "title": "Помыть посуду",
            "user_id": 99,
            "category_id": 1,
            "priority": 2,
            "due_date": "2026-09-25",
            "status": "Запланировано",
        }],
    )
    with pytest.raises(StorageError):
        load_chores([], categories, filename)


def test_save_and_load_categories(tmp_path):
    """Категории сохраняются и загружаются как объекты Category."""
    filename = str(tmp_path / "categories.json")
    categories = [Category(1, "Кухня")]
    save_categories(categories, filename)
    loaded = load_categories(filename)
    assert loaded[0].name == "Кухня"
    assert loaded[0].id == 1
