"""Формы категорий домашних дел."""

from django import forms

from categories.models import Category
from home_tasks.form_widgets import apply_bootstrap_widgets


class CategoryForm(forms.ModelForm):
    """Форма создания и редактирования категории."""

    class Meta:
        model = Category
        fields = ["name", "image"]
        labels = {
            "name": "Название",
            "image": "Изображение",
        }
        help_texts = {
            "name": "Название группы однотипных домашних дел.",
            "image": "Необязательная картинка категории.",
        }

    def __init__(self, *args, **kwargs):
        """Подключить Bootstrap-классы к виджетам."""
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)
