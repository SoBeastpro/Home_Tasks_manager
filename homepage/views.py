"""Представления главной страницы."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    """Показать главную страницу сервиса."""
    return render(request, "homepage/index.html")


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    """Вернуть свою HTML-страницу для неизвестного адреса."""
    return render(request, "404.html", status=404)
