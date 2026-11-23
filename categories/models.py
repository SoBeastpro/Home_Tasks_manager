"""Модель категории домашних дел."""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode


def build_category_slug(name: str, pk: int) -> str:
    """Собрать латинский slug категории по названию и id."""
    base_slug = slugify(unidecode(name)) or "category"
    return f"{base_slug}-{pk}"


class Category(models.Model):
    """Группа однотипных домашних дел."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название категории",
    )
    slug = models.SlugField(
        max_length=180,
        unique=True,
        editable=False,
        verbose_name="URL-идентификатор",
    )

    def save(self, *args, **kwargs) -> None:
        """Сохранить категорию и при необходимости заполнить slug."""
        if not self.slug:
            if self.pk:
                self.slug = build_category_slug(self.name, self.pk)
            else:
                super().save(*args, **kwargs)
                self.slug = build_category_slug(self.name, self.pk)
                super().save(update_fields=["slug"])
                return
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Вернуть адрес страницы категории."""
        return reverse("categories:detail", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        """Вернуть название категории."""
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
