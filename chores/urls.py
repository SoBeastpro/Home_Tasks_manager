"""Маршруты приложения дел."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.chore_list),
    path("<int:chore_id>/", views.chore_detail),
]
