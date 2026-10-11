"""ASGI-конфигурация проекта home_tasks."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "home_tasks.settings")

application = get_asgi_application()
