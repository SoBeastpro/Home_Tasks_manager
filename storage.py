"""Сохранение и загрузка данных проекта в JSON-файлах.

JSON хранит обычные данные. При загрузке они преобразуются в объекты
User, Category и Chore; при сохранении объекты снова превращаются
в словари. Связи дела с пользователем и категорией в файле хранятся
как идентификаторы user_id и category_id.
"""

import json
import os

from models import Category, Chore, User
from models.categories import find_category_by_id
from models.users import find_user_by_id

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


def load_users(filename: str = USERS_FILE) -> list[User]:
    """Загрузить пользователей и преобразовать их в объекты User."""
    users: list[User] = []
    for item in load_items(filename):
        try:
            users.append(User.from_data(item))
        except (KeyError, TypeError, ValueError) as error:
            raise StorageError(
                f"Некорректная запись пользователя: {item}"
            ) from error
    return users


def save_users(users: list[User], filename: str = USERS_FILE) -> None:
    """Сохранить объекты User в JSON-файл."""
    save_items(filename, [user.to_data() for user in users])


def load_categories(filename: str = CATEGORIES_FILE) -> list[Category]:
    """Загрузить категории и преобразовать их в объекты Category."""
    categories: list[Category] = []
    for item in load_items(filename):
        try:
            categories.append(Category.from_data(item))
        except (KeyError, TypeError, ValueError) as error:
            raise StorageError(
                f"Некорректная запись категории: {item}"
            ) from error
    return categories


def save_categories(
    categories: list[Category],
    filename: str = CATEGORIES_FILE,
) -> None:
    """Сохранить объекты Category в JSON-файл."""
    save_items(filename, [category.to_data() for category in categories])


def load_chores(
    users: list[User],
    categories: list[Category],
    filename: str = CHORES_FILE,
) -> list[Chore]:
    """Загрузить дела и восстановить связи с User и Category.

    Если пользователь или категория не найдены, дело не создаётся
    как корректный объект: возбуждается StorageError.
    """
    chores: list[Chore] = []
    for item in load_items(filename):
        try:
            user = find_user_by_id(users, int(item["user_id"]))
            category = find_category_by_id(
                categories,
                int(item["category_id"]),
            )
            chore = Chore(
                chore_id=int(item["id"]),
                title=str(item["title"]),
                user=user,
                category=category,
                due_date=item["due_date"],
                priority=int(item["priority"]),
                status=str(item["status"]),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise StorageError(
                f"Некорректная запись дела: {item}"
            ) from error
        chores.append(chore)
    return chores


def save_chores(chores: list[Chore], filename: str = CHORES_FILE) -> None:
    """Сохранить объекты Chore: вместо User и Category пишутся id."""
    save_items(filename, [chore.to_data() for chore in chores])
