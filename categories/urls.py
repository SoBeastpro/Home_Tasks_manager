"""Маршруты приложения категорий."""

from django.urls import path

from . import views

app_name = "categories"

urlpatterns = [
    path("", views.category_list, name="list"),
    path("create/", views.category_create, name="create"),
    path("statistics/", views.statistics, name="statistics"),
    path(
        "<slug:slug>/edit/",
        views.category_update,
        name="update",
    ),
    path("<slug:slug>/", views.category_detail, name="detail"),
]
