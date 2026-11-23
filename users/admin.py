"""Административный интерфейс пользователей."""

from django.contrib import admin

from chores.admin import ChoreInline

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Список, поиск и связанные дела пользователя."""

    list_display = ("id", "name", "email")
    list_display_links = ("name",)
    search_fields = ("name", "email")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("id",)
    inlines = (ChoreInline,)
