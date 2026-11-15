"""Модель пользователя предметной области."""

from django.db import models


class User(models.Model):
    """Член семьи, за которым закрепляются домашние дела."""

    name = models.CharField(
        max_length=200,
        verbose_name="Имя пользователя",
    )
    email = models.EmailField(
        verbose_name="Электронная почта",
    )

    def __str__(self) -> str:
        """Вернуть имя пользователя."""
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
