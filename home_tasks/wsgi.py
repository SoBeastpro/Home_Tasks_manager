"""WSGI-конфигурация проекта home_tasks."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "home_tasks.settings")

application = get_wsgi_application()
