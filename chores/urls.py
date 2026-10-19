"""Маршруты приложения дел."""

from django.urls import path

from . import views

app_name = "chores"

urlpatterns = [
    path("", views.chore_list, name="list"),
    path("<int:chore_id>/", views.chore_detail, name="detail"),
]
