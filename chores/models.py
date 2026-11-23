"""Модель домашнего дела и связи с пользователем и категорией."""

from datetime import date

from django.db import models
from django.db.models import Case, Value, When
from django.urls import reverse

from categories.models import Category
from users.models import User


PRIORITY_LABELS = {
    1: "Низкий",
    2: "Обычный",
    3: "Высокий",
}


class Status(models.TextChoices):
    """Статусы выполнения домашнего дела."""

    PLANNED = "Запланировано", "Запланировано"
    IN_PROGRESS = "В работе", "В работе"
    DONE = "Выполнено", "Выполнено"


STATUS_DONE = Status.DONE


class ChoreQuerySet(models.QuerySet):
    """Повторно используемые выборки дел."""

    def open(self):
        """Вернуть невыполненные дела."""
        return self.exclude(status=Status.DONE)

    def done(self):
        """Вернуть выполненные дела."""
        return self.filter(status=Status.DONE)

    def for_date(self, due_date):
        """Вернуть дела с указанным сроком."""
        return self.filter(due_date=due_date)

    def high_priority(self):
        """Вернуть дела с высоким приоритетом."""
        return self.filter(priority__gte=3)


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
        choices=Status.choices,
        default=Status.PLANNED,
        verbose_name="Статус",
    )
    is_high_priority = models.GeneratedField(
        expression=Case(
            When(priority__gte=3, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Высокий приоритет",
    )

    objects = ChoreQuerySet.as_manager()

    @property
    def priority_label(self) -> str:
        """Вернуть название уровня приоритета."""
        return PRIORITY_LABELS.get(self.priority, "Обычный")

    @property
    def is_done(self) -> bool:
        """Проверить, выполнено ли дело."""
        return self.status == Status.DONE

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
        self.status = Status.DONE
        self.save(update_fields=["status"])

    def get_absolute_url(self) -> str:
        """Вернуть адрес карточки дела."""
        return reverse("chores:detail", kwargs={"chore_id": self.pk})

    def __str__(self) -> str:
        """Вернуть название дела и срок."""
        return f"{self.title} — {self.due_date}"

    class Meta:
        ordering = ["due_date", "pk"]
        verbose_name = "Дело"
        verbose_name_plural = "Дела"
