"""Административный интерфейс домашних дел."""

from django.contrib import admin
from django.utils.html import format_html

from .models import Chore


class ChoreInline(admin.TabularInline):
    """Связанные дела на страницах пользователя и категории."""

    model = Chore
    fields = ("title", "due_date", "status", "priority")
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    """Список, поиск и фильтры дел."""

    list_display = (
        "id",
        "title",
        "user",
        "category",
        "due_date",
        "status",
        "priority",
        "is_high_priority",
        "site_link",
    )
    list_display_links = ("title",)
    list_editable = ("status",)
    search_fields = ("title", "user__name", "category__name")
    list_filter = ("status", "due_date", "priority", "category")
    ordering = ("-due_date",)
    list_per_page = 20
    list_select_related = ("user", "category")
    autocomplete_fields = ("user", "category")
    readonly_fields = ("id", "is_high_priority")
    view_on_site = True

    @admin.display(description="Страница на сайте")
    def site_link(self, obj: Chore):
        """Ссылка на публичную карточку дела."""
        return format_html(
            '<a href="{}" target="_blank">Открыть</a>',
            obj.get_absolute_url(),
        )
