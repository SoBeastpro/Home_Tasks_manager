"""Сущность «Пользователь»: члены семьи, отвечающие за домашние дела.

Пользователи хранятся в словаре, ключом которого является числовой
идентификатор, а значением — данные пользователя.
"""

from chores import is_chore_done


def get_next_user_id(users: dict[int, dict]) -> int:
    """Вернуть свободный идентификатор для нового пользователя."""
    if not users:
        return 1
    return max(users) + 1


def add_user(users: dict[int, dict], name: str) -> dict:
    """Добавить пользователя в словарь users и вернуть его данные.

    Вызывает ValueError, если имя пустое или уже занято.
    """
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Имя пользователя не может быть пустым")
    used_names = {user["name"].lower() for user in users.values()}
    if clean_name.lower() in used_names:
        raise ValueError(f"Пользователь «{clean_name}» уже существует")
    user_id = get_next_user_id(users)
    users[user_id] = {"id": user_id, "name": clean_name}
    return users[user_id]


def get_user(users: dict[int, dict], user_id: int) -> dict:
    """Вернуть данные пользователя по идентификатору.

    Вызывает KeyError, если пользователь не найден.
    """
    if user_id not in users:
        raise KeyError(f"Пользователь с номером {user_id} не найден")
    return users[user_id]


def get_user_name(users: dict[int, dict], user_id: int) -> str:
    """Вернуть имя пользователя или пометку, если он не найден."""
    user = users.get(user_id)
    if user is None:
        return "не назначен"
    return user["name"]


def search_users(users: dict[int, dict], query: str) -> list[dict]:
    """Найти пользователей по подстроке имени."""
    text = query.strip().lower()
    return [user for user in users.values() if text in user["name"].lower()]


def sort_users(users: dict[int, dict]) -> list[dict]:
    """Вернуть пользователей, упорядоченных по имени."""
    return sorted(users.values(), key=lambda user: user["name"].lower())


def get_user_workload(
    users: dict[int, dict],
    chores: list[dict],
) -> dict[str, int]:
    """Посчитать количество невыполненных дел каждого пользователя."""
    workload = {user["name"]: 0 for user in sort_users(users)}
    for chore in chores:
        if is_chore_done(chore):
            continue
        name = get_user_name(users, chore["user_id"])
        workload[name] = workload.get(name, 0) + 1
    return workload
