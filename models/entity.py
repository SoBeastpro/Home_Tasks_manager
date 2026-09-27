"""Базовый класс именованной сущности предметной области.

Пользователь и категория являются именованными сущностями:
у каждой есть идентификатор, название и строковое представление.
Общие данные и поведение вынесены в класс Entity, чтобы не дублировать
их в наследниках.
"""


class Entity:
    """Именованная сущность с идентификатором и названием."""

    def __init__(self, entity_id: int, name: str) -> None:
        """Сохранить идентификатор и название сущности."""
        self.id = entity_id
        self.name = name

    def matches(self, query: str) -> bool:
        """Проверить, встречается ли подстрока в названии сущности."""
        return query.strip().lower() in self.name.lower()

    def __eq__(self, other: object) -> bool:
        """Сравнить сущности по классу и идентификатору."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.id == other.id

    def __str__(self) -> str:
        """Вернуть строковое представление сущности."""
        return f"{self.__class__.__name__} №{self.id}: {self.name}"
