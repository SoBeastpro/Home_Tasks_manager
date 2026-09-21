"""Сохранение и загрузка данных проекта в JSON-файлах.

Чтение и запись выполняются через контекстный менеджер with, поэтому
файл закрывается даже при возникновении ошибки. Отсутствие файла
считается пустым набором данных, а поврежденный JSON приводит
к исключению StorageError.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
CHORES_FILE = os.path.join(DATA_DIR, "chores.json")


class StorageError(Exception):
    """Ошибка чтения или записи файла данных."""


def load_items(filename: str) -> list[dict]:
    """Прочитать список записей из JSON-файла.

    Если файл отсутствует, возвращается пустой список.
    Вызывает StorageError, если файл поврежден или содержит не список.
    """
    try:
        with open(filename, "r", encoding="utf-8") as data_file:
            items = json.load(data_file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise StorageError(
            f"Файл {filename} поврежден: {error}"
        ) from error
    except OSError as error:
        raise StorageError(
            f"Не удалось прочитать файл {filename}: {error}"
        ) from error
    if not isinstance(items, list):
        raise StorageError(f"Файл {filename} должен содержать список")
    return items


def save_items(filename: str, items: list[dict]) -> None:
    """Записать список записей в JSON-файл.

    Вызывает StorageError, если файл не удалось сохранить.
    """
    directory = os.path.dirname(filename)
    try:
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as data_file:
            json.dump(items, data_file, ensure_ascii=False, indent=2)
    except OSError as error:
        raise StorageError(
            f"Не удалось сохранить файл {filename}: {error}"
        ) from error


def items_to_dict(items: list[dict]) -> dict[int, dict]:
    """Преобразовать список записей в словарь по идентификатору.

    Вызывает StorageError, если в записи нет корректного поля id.
    """
    result: dict[int, dict] = {}
    for item in items:
        try:
            item_id = int(item["id"])
        except (KeyError, TypeError, ValueError) as error:
            raise StorageError(f"Некорректная запись: {item}") from error
        item["id"] = item_id
        result[item_id] = item
    return result


def load_users() -> dict[int, dict]:
    """Загрузить пользователей из файла data/users.json."""
    return items_to_dict(load_items(USERS_FILE))


def save_users(users: dict[int, dict]) -> None:
    """Сохранить пользователей в файл data/users.json."""
    save_items(USERS_FILE, list(users.values()))


def load_categories() -> dict[int, dict]:
    """Загрузить категории из файла data/categories.json."""
    return items_to_dict(load_items(CATEGORIES_FILE))


def save_categories(categories: dict[int, dict]) -> None:
    """Сохранить категории в файл data/categories.json."""
    save_items(CATEGORIES_FILE, list(categories.values()))


def load_chores() -> list[dict]:
    """Загрузить домашние дела из файла data/chores.json."""
    return load_items(CHORES_FILE)


def save_chores(chores: list[dict]) -> None:
    """Сохранить домашние дела в файл data/chores.json."""
    save_items(CHORES_FILE, chores)
