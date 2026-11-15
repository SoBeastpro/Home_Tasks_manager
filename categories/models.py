"""Модель категории домашних дел."""

from django.db import models


class Category(models.Model):
    """Группа однотипных домашних дел."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название категории",
    )

    def __str__(self) -> str:
        """Вернуть название категории."""
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
