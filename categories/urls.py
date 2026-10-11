"""Маршруты приложения категорий."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.category_list, name="categories"),
    path(
        "<int:category_id>/",
        views.category_detail,
        name="category_detail",
    ),
]
