"""Маршруты приложения дел."""

from django.urls import path

from . import views

app_name = "chores"

urlpatterns = [
    path("", views.chore_list, name="list"),
    path("open/", views.open_chores, name="open"),
    path("by-date/", views.chores_by_date, name="by_date"),
    path("create/", views.chore_create, name="create"),
    path(
        "<int:chore_id>/edit/",
        views.chore_update,
        name="update",
    ),
    path(
        "<int:chore_id>/complete/",
        views.chore_complete,
        name="complete",
    ),
    path("<int:chore_id>/", views.chore_detail, name="detail"),
]
