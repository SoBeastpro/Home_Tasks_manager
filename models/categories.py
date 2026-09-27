"""Класс Category и функции работы с коллекцией категорий."""

from .entity import Entity


class Category(Entity):
    """Группа однотипных домашних дел."""

    def __init__(self, category_id: int, name: str) -> None:
        """Создать объект категории."""
        super().__init__(category_id, self.validate_name(name))

    @staticmethod
    def validate_name(name: str) -> str:
        """Проверить название категории и вернуть его без пробелов."""
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Название категории не может быть пустым")
        return clean_name

    @classmethod
    def from_data(cls, data: dict) -> "Category":
        """Создать категорию из словаря данных JSON."""
        return cls(
            category_id=int(data["id"]),
            name=str(data["name"]),
        )

    def to_data(self) -> dict:
        """Вернуть данные категории для сохранения в JSON."""
        return {"id": self.id, "name": self.name}

    def __str__(self) -> str:
        """Вернуть строковое представление категории."""
        return f"Категория №{self.id}: {self.name}"


def get_next_category_id(categories: list[Category]) -> int:
    """Вернуть свободный идентификатор для новой категории."""
    if not categories:
        return 1
    return max(category.id for category in categories) + 1


def add_category(categories: list[Category], name: str) -> Category:
    """Создать объект Category, добавить его в коллекцию и вернуть.

    Вызывает ValueError, если название пустое или уже используется.
    """
    clean_name = Category.validate_name(name)
    used_names = {category.name.lower() for category in categories}
    if clean_name.lower() in used_names:
        raise ValueError(f"Категория «{clean_name}» уже существует")
    category = Category(get_next_category_id(categories), clean_name)
    categories.append(category)
    return category


def find_category_by_id(
    categories: list[Category],
    category_id: int,
) -> Category:
    """Найти категорию по идентификатору.

    Вызывает KeyError, если категория не найдена.
    """
    for category in categories:
        if category.id == category_id:
            return category
    raise KeyError(f"Категория с номером {category_id} не найдена")


def get_category(
    categories: list[Category],
    category_id: int,
) -> Category:
    """Вернуть категорию по идентификатору."""
    return find_category_by_id(categories, category_id)


def get_category_name(
    categories: list[Category],
    category_id: int,
) -> str:
    """Вернуть название категории или пометку, если она не найдена."""
    try:
        return find_category_by_id(categories, category_id).name
    except KeyError:
        return "без категории"


def find_category(categories: list[Category], query: str) -> list[Category]:
    """Найти категории по подстроке названия."""
    return [category for category in categories if category.matches(query)]


def search_categories(
    categories: list[Category],
    query: str,
) -> list[Category]:
    """Найти категории по подстроке названия."""
    return find_category(categories, query)


def sort_categories(categories: list[Category]) -> list[Category]:
    """Вернуть категории, упорядоченные по названию."""
    return sorted(categories, key=lambda category: category.name.lower())


def count_chores_by_category(
    categories: list[Category],
    chores: list,
) -> dict[str, int]:
    """Посчитать количество дел в каждой категории."""
    counters = {
        category.name: 0 for category in sort_categories(categories)
    }
    for chore in chores:
        name = chore.category.name
        counters[name] = counters.get(name, 0) + 1
    return counters


def show_categories(categories: list[Category]) -> None:
    """Вывести информацию об объектах Category."""
    if not categories:
        print("Категории не добавлены.")
        return
    for category in sort_categories(categories):
        print(f"  {category}")
