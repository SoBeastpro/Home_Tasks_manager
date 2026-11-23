"""Административный интерфейс категорий."""

from django.contrib import admin
from django.utils.html import format_html

from chores.admin import ChoreInline

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Список, поиск и связанные дела категории."""

    list_display = ("id", "name", "slug", "site_link")
    list_display_links = ("name",)
    search_fields = ("name", "slug")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("id", "slug")
    inlines = (ChoreInline,)
    view_on_site = True

    @admin.display(description="Страница на сайте")
    def site_link(self, obj: Category):
        """Ссылка на публичную страницу категории."""
        if not obj.slug:
            return "—"
        return format_html(
            '<a href="{}" target="_blank">Открыть</a>',
            obj.get_absolute_url(),
        )
