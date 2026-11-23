"""Формы фильтрации и редактирования домашних дел."""

from django import forms
from django.utils import timezone

from categories.models import Category
from chores.models import PRIORITY_LABELS, Chore
from home_tasks.form_widgets import apply_bootstrap_widgets
from users.models import User

PRIORITY_CHOICES = [
    (level, label)
    for level, label in PRIORITY_LABELS.items()
]


class ChoreFilterForm(forms.Form):
    """GET-форма поиска и фильтрации списка дел."""

    q = forms.CharField(
        required=False,
        label="Поиск",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Название или исполнитель",
            },
        ),
    )
    date = forms.DateField(
        required=False,
        label="Срок",
        widget=forms.DateInput(
            attrs={"type": "date"},
            format="%Y-%m-%d",
        ),
        input_formats=["%Y-%m-%d"],
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.order_by("name"),
        empty_label="Все категории",
        label="Категория",
    )
    user = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.order_by("name"),
        empty_label="Все исполнители",
        label="Исполнитель",
    )
    sort = forms.ChoiceField(
        required=False,
        label="Сортировка",
        choices=[
            ("date", "По сроку"),
            ("title", "По названию"),
            ("user", "По исполнителю"),
            ("category", "По категории"),
            ("priority", "По приоритету"),
        ],
    )

    def __init__(self, *args, **kwargs):
        """Подключить Bootstrap-классы к виджетам."""
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class ChoreForm(forms.ModelForm):
    """Форма создания и редактирования домашнего дела."""

    class Meta:
        model = Chore
        fields = [
            "title",
            "user",
            "category",
            "priority",
            "due_date",
        ]
        labels = {
            "title": "Название",
            "user": "Исполнитель",
            "category": "Категория",
            "priority": "Приоритет",
            "due_date": "Срок выполнения",
        }
        help_texts = {
            "title": "Кратко опишите домашнее дело.",
            "due_date": "Укажите дату, к которой дело нужно выполнить.",
            "category": (
                "В одной категории на одну дату может быть только "
                "одно невыполненное дело."
            ),
        }
        widgets = {
            "due_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
            "priority": forms.Select(choices=PRIORITY_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        """Настроить виджеты и допустимые значения приоритета."""
        super().__init__(*args, **kwargs)
        self.fields["due_date"].input_formats = ["%Y-%m-%d"]
        self.fields["priority"].choices = PRIORITY_CHOICES
        apply_bootstrap_widgets(self)

    def clean_due_date(self):
        """Запретить назначение нового дела на прошедшую дату."""
        due_date = self.cleaned_data["due_date"]
        if due_date < timezone.localdate():
            original = self.instance.due_date if self.instance.pk else None
            if original != due_date:
                raise forms.ValidationError(
                    "Нельзя назначить дело на прошедшую дату.",
                )
        return due_date
