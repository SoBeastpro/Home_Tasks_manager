"""Сервис учета домашних дел — точка запуска приложения.

Модуль организует меню и пользовательские сценарии. Данные предметной
области передаются как коллекции объектов User, Category и Chore.
Создание и поиск объектов выполняются функциями пакета models,
а не непосредственно в main.py.
"""

from datetime import date

from models import Category, Chore, User
from models.categories import (
    add_category,
    count_chores_by_category,
    find_category_by_id,
    sort_categories,
)
from models.chores import (
    add_chore,
    complete_chore,
    count_chores_by_status,
    delete_chore,
    filter_chores_by_category,
    filter_chores_by_user,
    find_chore,
    get_chore_status,
    get_chores_for_date,
    get_overdue_chores,
    search_chores,
    set_chore_status,
    sort_chores,
)
from models.statuses import STATUS_CLASSES, status_by_number
from models.users import (
    add_user,
    find_user_by_id,
    get_user_workload,
    sort_users,
)
from storage import (
    StorageError,
    load_categories,
    load_chores,
    load_users,
    save_categories,
    save_chores,
    save_users,
)
from utils import (
    enable_utf8_output,
    format_date,
    input_date,
    input_int,
    input_text,
)

MENU = """
=== Сервис учета домашних дел ===
--- Дела ---
1. Показать все дела
2. Найти дело по названию
3. Показать дела пользователя
4. Показать дела категории
5. Показать дела на дату
6. Показать карточку дела
7. Добавить дело
8. Изменить статус дела
9. Отметить дело выполненным
10. Удалить дело
11. Показать просроченные дела
--- Справочники ---
12. Показать пользователей
13. Добавить пользователя
14. Показать категории
15. Добавить категорию
--- Отчеты ---
16. Показать статистику
0. Выход"""

TABLE_HEADER = (
    f"{'ID':<4}{'Дело':<28}{'Категория':<14}"
    f"{'Исполнитель':<13}{'Статус':<15}{'Срок':<12}Приоритет"
)

DATA_CHANGING_ACTIONS = frozenset({7, 8, 9, 10, 13, 15})


def format_chore_row(chore: Chore) -> str:
    """Вернуть строку таблицы для одного дела."""
    return (
        f"{chore.id:<4}"
        f"{chore.title[:26]:<28}"
        f"{chore.category.name[:12]:<14}"
        f"{chore.user.name[:11]:<13}"
        f"{str(chore.status):<15}"
        f"{format_date(chore.due_date):<12}"
        f"{chore.priority_label}"
    )


def show_chores_table(
    chores: list[Chore],
    title: str = "Список дел",
) -> None:
    """Вывести дела в виде таблицы, упорядочив их по сроку."""
    print(f"\n{title} ({len(chores)}):")
    if not chores:
        print("Дел не найдено.")
        return
    print(TABLE_HEADER)
    for chore in sort_chores(chores):
        print(format_chore_row(chore))


def show_chore_card(chore: Chore) -> None:
    """Вывести подробную карточку дела.

    Карточка повторяет начальный сценарий ПР1: статус, срок и подсказка
    формируются функциями, перенесёнными из первой практической работы.
    """
    days_left = chore.days_left(date.today())
    print(f"\n{chore}")
    print(f"Категория: {chore.category.name}")
    print(f"Исполнитель: {chore.user.name}")
    print(f"Приоритет: {chore.priority_label}")
    print(f"Срок: {format_date(chore.due_date)}")
    print(f"Осталось дней: {days_left}")
    print(f"Статус: {chore.status}")
    print(f"Отметка о выполнении: {get_chore_status(chore.is_done())}")
    print(chore.deadline_message(date.today()))
    if days_left <= 2 and not chore.is_done():
        print("Внимание: дело требует срочного выполнения!")


def choose_user(users: list[User]) -> User:
    """Показать пользователей и вернуть выбранный объект User."""
    if not users:
        raise ValueError("Сначала добавьте хотя бы одного пользователя")
    print("Пользователи:")
    for user in sort_users(users):
        print(f"  {user.id}. {user.name}")
    return find_user_by_id(users, input_int("Номер пользователя: ", 1))


def choose_category(categories: list[Category]) -> Category:
    """Показать категории и вернуть выбранный объект Category."""
    if not categories:
        raise ValueError("Сначала добавьте хотя бы одну категорию")
    print("Категории:")
    for category in sort_categories(categories):
        print(f"  {category.id}. {category.name}")
    category_id = input_int("Номер категории: ", 1)
    return find_category_by_id(categories, category_id)


def handle_show_chores(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Вывести все дела."""
    show_chores_table(chores, "Все дела")


def handle_search_chores(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Найти дела по части названия."""
    query = input_text("Часть названия дела: ")
    found = search_chores(chores, query)
    show_chores_table(found, f"Результаты поиска «{query}»")


def handle_user_chores(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Вывести дела выбранного пользователя."""
    user = choose_user(users)
    found = filter_chores_by_user(chores, user.id)
    show_chores_table(found, f"Дела пользователя {user.name}")


def handle_category_chores(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Вывести дела выбранной категории."""
    category = choose_category(categories)
    found = filter_chores_by_category(chores, category.id)
    show_chores_table(found, f"Дела категории {category.name}")


def handle_chores_for_date(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Вывести дела, запланированные на указанную дату."""
    day = input_date("Дата (ДД.ММ.ГГГГ): ")
    found = get_chores_for_date(chores, day)
    show_chores_table(found, f"Дела на {format_date(day)}")


def handle_chore_card(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Вывести карточку выбранного дела."""
    show_chore_card(find_chore(chores, input_int("Номер дела: ", 1)))


def handle_add_chore(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Добавить новое дело, связав его с User и Category."""
    title = input_text("Название дела: ")
    user = choose_user(users)
    category = choose_category(categories)
    due_date = input_date("Срок выполнения (ДД.ММ.ГГГГ): ")
    priority = input_int("Приоритет (1 — низкий, 3 — высокий): ", 1, 3)
    chore = add_chore(chores, title, user, category, due_date, priority)
    print(f"Добавлено дело №{chore.id}: {chore.title}")


def handle_change_status(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Изменить статус выбранного дела."""
    chore = find_chore(chores, input_int("Номер дела: ", 1))
    print(f"Текущий статус: {chore.status}")
    for number, status_class in enumerate(STATUS_CLASSES, start=1):
        print(f"  {number}. {status_class.name}")
    choice = input_int("Новый статус: ", 1, len(STATUS_CLASSES))
    updated = set_chore_status(chores, chore.id, status_by_number(choice))
    print(f"Статус дела №{updated.id}: {updated.status}")


def handle_complete_chore(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Отметить дело выполненным."""
    chore = complete_chore(chores, input_int("Номер дела: ", 1))
    print(f"Дело «{chore.title}» отмечено как выполненное.")


def handle_delete_chore(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Удалить дело."""
    chore = delete_chore(chores, input_int("Номер дела: ", 1))
    print(f"Дело «{chore.title}» удалено.")


def handle_overdue_chores(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Вывести просроченные дела."""
    overdue = get_overdue_chores(chores, date.today())
    show_chores_table(overdue, "Просроченные дела")


def handle_show_users(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Вывести пользователей и их текущую нагрузку."""
    if not users:
        print("\nПользователи не добавлены.")
        return
    workload = get_user_workload(users, chores)
    print(f"\nПользователи ({len(users)}):")
    for user in sort_users(users):
        count = workload.get(user.name, 0)
        print(f"  {user.id}. {user.name} — невыполненных дел: {count}")


def handle_add_user(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Добавить пользователя."""
    name = input_text("Имя пользователя: ")
    email = input("Электронная почта (необязательно): ").strip()
    user = add_user(users, name, email)
    print(f"Добавлен {user}")


def handle_show_categories(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Вывести категории и количество дел в каждой из них."""
    if not categories:
        print("\nКатегории не добавлены.")
        return
    counters = count_chores_by_category(categories, chores)
    print(f"\nКатегории ({len(categories)}):")
    for category in sort_categories(categories):
        count = counters.get(category.name, 0)
        print(f"  {category.id}. {category.name} — дел: {count}")


def handle_add_category(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Добавить категорию."""
    category = add_category(categories, input_text("Название категории: "))
    print(f"Добавлена {category}")


def handle_statistics(
    chores: list[Chore],
    users: list[User],
    categories: list[Category],
) -> None:
    """Вывести статистику по делам, категориям и исполнителям."""
    print(f"\nВсего дел: {len(chores)}")
    print("По статусам:")
    for status, count in count_chores_by_status(chores).items():
        print(f"  {status}: {count}")
    print("По категориям:")
    for name, count in count_chores_by_category(categories, chores).items():
        print(f"  {name}: {count}")
    print("Невыполненных дел по исполнителям:")
    for name, count in get_user_workload(users, chores).items():
        print(f"  {name}: {count}")
    overdue = get_overdue_chores(chores, date.today())
    print(f"Просрочено дел: {len(overdue)}")


ACTIONS = {
    1: handle_show_chores,
    2: handle_search_chores,
    3: handle_user_chores,
    4: handle_category_chores,
    5: handle_chores_for_date,
    6: handle_chore_card,
    7: handle_add_chore,
    8: handle_change_status,
    9: handle_complete_chore,
    10: handle_delete_chore,
    11: handle_overdue_chores,
    12: handle_show_users,
    13: handle_add_user,
    14: handle_show_categories,
    15: handle_add_category,
    16: handle_statistics,
}


def save_all(
    users: list[User],
    categories: list[Category],
    chores: list[Chore],
) -> None:
    """Сохранить все данные проекта в JSON-файлы."""
    save_users(users)
    save_categories(categories)
    save_chores(chores)


def main() -> None:
    """Точка запуска: загрузка объектов, цикл меню и сохранение."""
    enable_utf8_output()
    try:
        users = load_users()
        categories = load_categories()
        chores = load_chores(users, categories)
    except StorageError as error:
        print(f"Не удалось загрузить данные: {error}")
        return
    print(
        f"Данные загружены: дел — {len(chores)}, "
        f"пользователей — {len(users)}, категорий — {len(categories)}."
    )
    while True:
        print(MENU)
        try:
            choice = input_int("Выберите действие: ", 0, max(ACTIONS))
            if choice == 0:
                print("Работа завершена.")
                break
            ACTIONS[choice](chores, users, categories)
            if choice in DATA_CHANGING_ACTIONS:
                save_all(users, categories, chores)
        except KeyError as error:
            print(f"Ошибка: {error.args[0]}")
        except ValueError as error:
            print(f"Ошибка: {error}")
        except StorageError as error:
            print(f"Ошибка работы с файлами данных: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена.")
            break


if __name__ == "__main__":
    main()
