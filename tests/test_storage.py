"""Автоматические тесты сохранения и загрузки данных проекта."""

import pytest

from storage import StorageError, items_to_dict, load_items, save_items


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


def test_items_to_dict():
    """Список записей превращается в словарь по идентификатору."""
    users = items_to_dict([{"id": "2", "name": "Мария"}])
    assert users == {2: {"id": 2, "name": "Мария"}}


def test_items_to_dict_without_id():
    """Запись без идентификатора приводит к StorageError."""
    with pytest.raises(StorageError):
        items_to_dict([{"name": "Мария"}])
