"""Сущность «Категория»: группы однотипных домашних дел.

Категории хранятся в словаре, ключом которого является числовой
идентификатор, а значением — данные категории.
"""


def get_next_category_id(categories: dict[int, dict]) -> int:
    """Вернуть свободный идентификатор для новой категории."""
    if not categories:
        return 1
    return max(categories) + 1


def add_category(categories: dict[int, dict], name: str) -> dict:
    """Добавить категорию в словарь categories и вернуть ее данные.

    Вызывает ValueError, если название пустое или уже используется.
    """
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Название категории не может быть пустым")
    used_names = {
        category["name"].lower() for category in categories.values()
    }
    if clean_name.lower() in used_names:
        raise ValueError(f"Категория «{clean_name}» уже существует")
    category_id = get_next_category_id(categories)
    categories[category_id] = {"id": category_id, "name": clean_name}
    return categories[category_id]


def get_category(categories: dict[int, dict], category_id: int) -> dict:
    """Вернуть данные категории по идентификатору.

    Вызывает KeyError, если категория не найдена.
    """
    if category_id not in categories:
        raise KeyError(f"Категория с номером {category_id} не найдена")
    return categories[category_id]


def get_category_name(categories: dict[int, dict], category_id: int) -> str:
    """Вернуть название категории или пометку, если она не найдена."""
    category = categories.get(category_id)
    if category is None:
        return "без категории"
    return category["name"]


def search_categories(categories: dict[int, dict], query: str) -> list[dict]:
    """Найти категории по подстроке названия."""
    text = query.strip().lower()
    return [
        category
        for category in categories.values()
        if text in category["name"].lower()
    ]


def sort_categories(categories: dict[int, dict]) -> list[dict]:
    """Вернуть категории, упорядоченные по названию."""
    return sorted(
        categories.values(),
        key=lambda category: category["name"].lower(),
    )


def count_chores_by_category(
    categories: dict[int, dict],
    chores: list[dict],
) -> dict[str, int]:
    """Посчитать количество дел в каждой категории."""
    counters = {
        category["name"]: 0 for category in sort_categories(categories)
    }
    for chore in chores:
        name = get_category_name(categories, chore["category_id"])
        counters[name] = counters.get(name, 0) + 1
    return counters
