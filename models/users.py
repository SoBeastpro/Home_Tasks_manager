"""Класс User и функции работы с коллекцией пользователей."""

from .entity import Entity


class User(Entity):
    """Член семьи, отвечающий за выполнение домашних дел."""

    def __init__(self, user_id: int, name: str, email: str = "") -> None:
        """Создать объект пользователя."""
        super().__init__(user_id, self.validate_name(name))
        self.email = email.strip()

    @staticmethod
    def validate_name(name: str) -> str:
        """Проверить имя пользователя и вернуть его без пробелов по краям."""
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Имя пользователя не может быть пустым")
        return clean_name

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из словаря данных JSON."""
        return cls(
            user_id=int(data["id"]),
            name=str(data["name"]),
            email=str(data.get("email", "")),
        )

    def to_data(self) -> dict:
        """Вернуть данные пользователя для сохранения в JSON."""
        return {"id": self.id, "name": self.name, "email": self.email}

    def matches(self, query: str) -> bool:
        """Найти пользователя по части имени или адреса почты."""
        text = query.strip().lower()
        return text in self.name.lower() or text in self.email.lower()

    def __str__(self) -> str:
        """Вернуть строковое представление пользователя."""
        if self.email:
            return f"Пользователь №{self.id}: {self.name} <{self.email}>"
        return f"Пользователь №{self.id}: {self.name}"


def get_next_user_id(users: list[User]) -> int:
    """Вернуть свободный идентификатор для нового пользователя."""
    if not users:
        return 1
    return max(user.id for user in users) + 1


def add_user(users: list[User], name: str, email: str = "") -> User:
    """Создать объект User, добавить его в коллекцию и вернуть.

    Вызывает ValueError, если имя пустое или уже занято.
    """
    clean_name = User.validate_name(name)
    used_names = {user.name.lower() for user in users}
    if clean_name.lower() in used_names:
        raise ValueError(f"Пользователь «{clean_name}» уже существует")
    user = User(get_next_user_id(users), clean_name, email)
    users.append(user)
    return user


def find_user_by_id(users: list[User], user_id: int) -> User:
    """Найти пользователя по идентификатору.

    Вызывает KeyError, если пользователь не найден.
    """
    for user in users:
        if user.id == user_id:
            return user
    raise KeyError(f"Пользователь с номером {user_id} не найден")


def get_user(users: list[User], user_id: int) -> User:
    """Вернуть пользователя по идентификатору."""
    return find_user_by_id(users, user_id)


def get_user_name(users: list[User], user_id: int) -> str:
    """Вернуть имя пользователя или пометку, если он не найден."""
    try:
        return find_user_by_id(users, user_id).name
    except KeyError:
        return "не назначен"


def find_user(users: list[User], query: str) -> list[User]:
    """Найти пользователей по подстроке имени или почты."""
    return [user for user in users if user.matches(query)]


def search_users(users: list[User], query: str) -> list[User]:
    """Найти пользователей по подстроке имени."""
    return find_user(users, query)


def sort_users(users: list[User]) -> list[User]:
    """Вернуть пользователей, упорядоченных по имени."""
    return sorted(users, key=lambda user: user.name.lower())


def get_user_workload(
    users: list[User],
    chores: list,
) -> dict[str, int]:
    """Посчитать количество невыполненных дел каждого пользователя."""
    workload = {user.name: 0 for user in sort_users(users)}
    for chore in chores:
        if chore.is_done():
            continue
        workload[chore.user.name] = workload.get(chore.user.name, 0) + 1
    return workload


def show_users(users: list[User]) -> None:
    """Вывести информацию об объектах User."""
    if not users:
        print("Пользователи не добавлены.")
        return
    for user in sort_users(users):
        print(f"  {user}")
