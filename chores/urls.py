"""Маршруты приложения дел."""

from django.urls import path

from . import views

app_name = "chores"

urlpatterns = [
    path("", views.chore_list, name="list"),
    path("open/", views.open_chores, name="open"),
    path("by-date/", views.chores_by_date, name="by_date"),
    path("<int:chore_id>/", views.chore_detail, name="detail"),
]
