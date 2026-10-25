"""Перенос данных проекта из JSON-файлов в SQLite."""

import json
from pathlib import Path

from db.database import get_connection

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"
CATEGORIES_FILE = DATA_DIR / "categories.json"
CHORES_FILE = DATA_DIR / "chores.json"


def load_json(filename: Path) -> list:
    """Прочитать список записей из JSON-файла."""
    with open(filename, encoding="utf-8") as data_file:
        return json.load(data_file)


def import_users(conn) -> None:
    """Перенести пользователей в таблицу users."""
    users = load_json(USERS_FILE)
    conn.executemany(
        """
        INSERT INTO users (id, name, email)
        VALUES (?, ?, ?)
        """,
        [
            (user["id"], user["name"], user["email"])
            for user in users
        ],
    )


def import_categories(conn) -> None:
    """Перенести категории в таблицу categories."""
    categories = load_json(CATEGORIES_FILE)
    conn.executemany(
        """
        INSERT INTO categories (id, name)
        VALUES (?, ?)
        """,
        [
            (category["id"], category["name"])
            for category in categories
        ],
    )


def import_chores(conn) -> None:
    """Перенести дела в таблицу chores."""
    chores = load_json(CHORES_FILE)
    conn.executemany(
        """
        INSERT INTO chores (
            id,
            title,
            user_id,
            category_id,
            priority,
            due_date,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                chore["id"],
                chore["title"],
                chore["user_id"],
                chore["category_id"],
                chore["priority"],
                chore["due_date"],
                chore["status"],
            )
            for chore in chores
        ],
    )


def main() -> None:
    """Очистить таблицы и загрузить данные из JSON."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM chores")
        conn.execute("DELETE FROM categories")
        conn.execute("DELETE FROM users")
        import_users(conn)
        import_categories(conn)
        import_chores(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
