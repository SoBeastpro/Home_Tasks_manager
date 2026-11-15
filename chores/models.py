"""Модель домашнего дела и связи с пользователем и категорией."""

from datetime import date

from django.db import models

from categories.models import Category
from users.models import User


PRIORITY_LABELS = {
    1: "Низкий",
    2: "Обычный",
    3: "Высокий",
}

STATUS_PLANNED = "Запланировано"
STATUS_IN_PROGRESS = "В работе"
STATUS_DONE = "Выполнено"
STATUS_CHOICES = [
    (STATUS_PLANNED, STATUS_PLANNED),
    (STATUS_IN_PROGRESS, STATUS_IN_PROGRESS),
    (STATUS_DONE, STATUS_DONE),
]


class Chore(models.Model):
    """Домашнее дело, закреплённое за пользователем и категорией."""

    title = models.CharField(
        max_length=200,
        verbose_name="Название дела",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="chores",
        verbose_name="Исполнитель",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="chores",
        verbose_name="Категория",
    )
    priority = models.PositiveIntegerField(
        default=2,
        verbose_name="Приоритет",
    )
    due_date = models.DateField(
        verbose_name="Срок выполнения",
    )
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default=STATUS_PLANNED,
        verbose_name="Статус",
    )

    @property
    def priority_label(self) -> str:
        """Вернуть название уровня приоритета."""
        return PRIORITY_LABELS.get(self.priority, "Обычный")

    @property
    def is_done(self) -> bool:
        """Проверить, выполнено ли дело."""
        return self.status == STATUS_DONE

    def days_left(self) -> int:
        """Вернуть число дней до срока выполнения."""
        return (self.due_date - date.today()).days

    def deadline_message(self) -> str:
        """Вернуть подсказку о сроке выполнения."""
        if self.is_done:
            return "Дело выполнено, срок уже не важен"
        leftover = self.days_left()
        if leftover < 0:
            return f"Срок пропущен {-leftover} дн. назад"
        if leftover == 0:
            return "Сделать сегодня"
        if leftover <= 2:
            return "Срок скоро истекает"
        return "Времени достаточно"

    def complete(self) -> None:
        """Отметить дело выполненным и сохранить статус."""
        self.status = STATUS_DONE
        self.save(update_fields=["status"])

    def __str__(self) -> str:
        """Вернуть название дела и срок."""
        return f"{self.title} — {self.due_date}"

    class Meta:
        ordering = ["due_date", "pk"]
        verbose_name = "Дело"
        verbose_name_plural = "Дела"
