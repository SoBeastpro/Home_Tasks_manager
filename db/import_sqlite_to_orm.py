"""Перенос данных из базы ПР7 в таблицы Django ORM."""

import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

import django
from django.db import transaction

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
SOURCE_DB = BASE_DIR / "data" / "home_tasks.sqlite"

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "home_tasks.settings",
)
django.setup()

from categories.models import Category  # noqa: E402
from chores.models import Chore  # noqa: E402
from users.models import User  # noqa: E402


def main() -> None:
    """Прочитать исходную базу и сохранить записи через ORM."""
    if not SOURCE_DB.exists():
        raise FileNotFoundError(
            f"Исходная база не найдена: {SOURCE_DB}"
        )

    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row
        users = connection.execute(
            """
            SELECT id, name, email
            FROM users
            ORDER BY id
            """
        ).fetchall()
        categories = connection.execute(
            """
            SELECT id, name
            FROM categories
            ORDER BY id
            """
        ).fetchall()
        chores = connection.execute(
            """
            SELECT
                id,
                title,
                user_id,
                category_id,
                priority,
                due_date,
                status
            FROM chores
            ORDER BY id
            """
        ).fetchall()

        with transaction.atomic():
            for row in users:
                User.objects.update_or_create(
                    pk=row["id"],
                    defaults={
                        "name": row["name"],
                        "email": row["email"],
                    },
                )
            for row in categories:
                Category.objects.update_or_create(
                    pk=row["id"],
                    defaults={"name": row["name"]},
                )
            for row in chores:
                Chore.objects.update_or_create(
                    pk=row["id"],
                    defaults={
                        "title": row["title"],
                        "user_id": row["user_id"],
                        "category_id": row["category_id"],
                        "priority": row["priority"],
                        "due_date": date.fromisoformat(row["due_date"]),
                        "status": row["status"],
                    },
                )

    print("Перенос данных завершён.")
    print(f"Пользователей: {User.objects.count()}")
    print(f"Категорий: {Category.objects.count()}")
    print(f"Дел: {Chore.objects.count()}")


if __name__ == "__main__":
    main()
