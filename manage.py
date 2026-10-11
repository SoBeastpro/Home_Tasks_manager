#!/usr/bin/env python
"""Утилита командной строки Django."""

import os
import sys


def main() -> None:
    """Запустить административную команду Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "home_tasks.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. Проверьте установку "
            "и активацию виртуального окружения."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
