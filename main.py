"""Сервис учета домашних дел — точка запуска приложения.

Модуль содержит функции вывода данных, обработчики пунктов меню
и основной цикл взаимодействия с пользователем. Данные о делах,
пользователях и категориях загружаются из JSON-файлов каталога data
при запуске и сохраняются после каждого изменения.
"""

from datetime import date

from categories import (
    add_category,
    count_chores_by_category,
    get_category,
    get_category_name,
    sort_categories,
)
from chores import (
    add_chore,
    complete_chore,
    count_chores_by_status,
    delete_chore,
    filter_chores_by_category,
    filter_chores_by_user,
    find_chore,
    get_chore_status,
    get_chores_for_date,
    get_days_left,
    get_deadline_message,
    get_overdue_chores,
    get_priority_label,
    is_chore_done,
    search_chores,
    set_chore_status,
    sort_chores,
)
from statuses import STATUSES, status_by_number
from storage import (
    StorageError,
    load_categories,
    load_chores,
    load_users,
    save_categories,
    save_chores,
    save_users,
)
from users import (
    add_user,
    get_user,
    get_user_name,
    get_user_workload,
    sort_users,
)
from utils import (
    enable_utf8_output,
    format_date,
    input_date,
    input_int,
    input_text,
)

Chores = list[dict]
Users = dict[int, dict]
Categories = dict[int, dict]

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

# Пункты меню, после которых данные нужно записать в файлы.
DATA_CHANGING_ACTIONS = frozenset({7, 8, 9, 10, 13, 15})


def format_chore_row(
    chore: dict, users: Users, categories: Categories
) -> str:
    """Вернуть строку таблицы для одного дела."""
    category_name = get_category_name(categories, chore["category_id"])
    user_name = get_user_name(users, chore["user_id"])
    return (
        f"{chore['id']:<4}"
        f"{chore['title'][:26]:<28}"
        f"{category_name[:12]:<14}"
        f"{user_name[:11]:<13}"
        f"{chore['status']:<15}"
        f"{format_date(chore['due_date']):<12}"
        f"{get_priority_label(chore['priority'])}"
    )


def show_chores(
    chores: Chores,
    users: Users,
    categories: Categories,
    title: str = "Список дел",
) -> None:
    """Вывести дела в виде таблицы, упорядочив их по сроку выполнения."""
    print(f"\n{title} ({len(chores)}):")
    if not chores:
        print("Дел не найдено.")
        return
    print(TABLE_HEADER)
    for chore in sort_chores(chores):
        print(format_chore_row(chore, users, categories))


def show_chore_card(
    chore: dict, users: Users, categories: Categories
) -> None:
    """Вывести подробную карточку дела.

    Карточка повторяет начальный сценарий ПР1: статус, срок и подсказка
    формируются функциями, перенесенными из первой практической работы.
    """
    done = is_chore_done(chore)
    days_left = get_days_left(chore["due_date"], date.today())
    print(f"\nДело №{chore['id']}: {chore['title']}")
    print(f"Категория: {get_category_name(categories, chore['category_id'])}")
    print(f"Исполнитель: {get_user_name(users, chore['user_id'])}")
    print(f"Приоритет: {get_priority_label(chore['priority'])}")
    print(f"Срок: {format_date(chore['due_date'])}")
    print(f"Осталось дней: {days_left}")
    print(f"Статус: {chore['status']}")
    print(f"Отметка о выполнении: {get_chore_status(done)}")
    print(get_deadline_message(days_left, done))
    if days_left <= 2 and not done:
        print("Внимание: дело требует срочного выполнения!")


def choose_user(users: Users) -> int:
    """Показать пользователей и запросить номер исполнителя."""
    if not users:
        raise ValueError("Сначала добавьте хотя бы одного пользователя")
    print("Пользователи:")
    for user in sort_users(users):
        print(f"  {user['id']}. {user['name']}")
    user_id = input_int("Номер пользователя: ", 1)
    get_user(users, user_id)
    return user_id


def choose_category(categories: Categories) -> int:
    """Показать категории и запросить номер категории."""
    if not categories:
        raise ValueError("Сначала добавьте хотя бы одну категорию")
    print("Категории:")
    for category in sort_categories(categories):
        print(f"  {category['id']}. {category['name']}")
    category_id = input_int("Номер категории: ", 1)
    get_category(categories, category_id)
    return category_id


def handle_show_chores(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Вывести все дела."""
    show_chores(chores, users, categories, "Все дела")


def handle_search_chores(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Найти дела по части названия."""
    query = input_text("Часть названия дела: ")
    found = search_chores(chores, query)
    show_chores(found, users, categories, f"Результаты поиска «{query}»")


def handle_user_chores(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Вывести дела выбранного пользователя."""
    user_id = choose_user(users)
    found = filter_chores_by_user(chores, user_id)
    title = f"Дела пользователя {get_user_name(users, user_id)}"
    show_chores(found, users, categories, title)


def handle_category_chores(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Вывести дела выбранной категории."""
    category_id = choose_category(categories)
    found = filter_chores_by_category(chores, category_id)
    title = f"Дела категории {get_category_name(categories, category_id)}"
    show_chores(found, users, categories, title)


def handle_chores_for_date(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Вывести дела, запланированные на указанную дату."""
    day = input_date("Дата (ДД.ММ.ГГГГ): ")
    found = get_chores_for_date(chores, day)
    show_chores(found, users, categories, f"Дела на {format_date(day)}")


def handle_chore_card(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Вывести карточку выбранного дела."""
    chore = find_chore(chores, input_int("Номер дела: ", 1))
    show_chore_card(chore, users, categories)


def handle_add_chore(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Добавить новое дело."""
    title = input_text("Название дела: ")
    user_id = choose_user(users)
    category_id = choose_category(categories)
    due_date = input_date("Срок выполнения (ДД.ММ.ГГГГ): ")
    priority = input_int("Приоритет (1 — низкий, 3 — высокий): ", 1, 3)
    chore = add_chore(
        chores, title, user_id, category_id, due_date, priority
    )
    print(f"Добавлено дело №{chore['id']}: {chore['title']}")


def handle_change_status(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Изменить статус выбранного дела."""
    chore_id = input_int("Номер дела: ", 1)
    chore = find_chore(chores, chore_id)
    print(f"Текущий статус: {chore['status']}")
    for number, status in enumerate(STATUSES, start=1):
        print(f"  {number}. {status}")
    choice = input_int("Новый статус: ", 1, len(STATUSES))
    updated = set_chore_status(chores, chore_id, status_by_number(choice))
    print(f"Статус дела №{updated['id']}: {updated['status']}")


def handle_complete_chore(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Отметить дело выполненным."""
    chore = complete_chore(chores, input_int("Номер дела: ", 1))
    print(f"Дело «{chore['title']}» отмечено как выполненное.")


def handle_delete_chore(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Удалить дело."""
    chore = delete_chore(chores, input_int("Номер дела: ", 1))
    print(f"Дело «{chore['title']}» удалено.")


def handle_overdue_chores(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Вывести просроченные дела."""
    overdue = get_overdue_chores(chores, date.today())
    show_chores(overdue, users, categories, "Просроченные дела")


def handle_show_users(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Вывести пользователей и их текущую нагрузку."""
    if not users:
        print("\nПользователи не добавлены.")
        return
    workload = get_user_workload(users, chores)
    print(f"\nПользователи ({len(users)}):")
    for user in sort_users(users):
        count = workload.get(user["name"], 0)
        print(f"  {user['id']}. {user['name']} — невыполненных дел: {count}")


def handle_add_user(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Добавить пользователя."""
    user = add_user(users, input_text("Имя пользователя: "))
    print(f"Добавлен пользователь №{user['id']}: {user['name']}")


def handle_show_categories(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Вывести категории и количество дел в каждой из них."""
    if not categories:
        print("\nКатегории не добавлены.")
        return
    counters = count_chores_by_category(categories, chores)
    print(f"\nКатегории ({len(categories)}):")
    for category in sort_categories(categories):
        count = counters.get(category["name"], 0)
        print(f"  {category['id']}. {category['name']} — дел: {count}")


def handle_add_category(
    chores: Chores, users: Users, categories: Categories
) -> None:
    """Добавить категорию."""
    category = add_category(categories, input_text("Название категории: "))
    print(f"Добавлена категория №{category['id']}: {category['name']}")


def handle_statistics(
    chores: Chores, users: Users, categories: Categories
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


def save_all(users: Users, categories: Categories, chores: Chores) -> None:
    """Сохранить все данные проекта в JSON-файлы."""
    save_users(users)
    save_categories(categories)
    save_chores(chores)


def main() -> None:
    """Точка запуска приложения: цикл меню и вызов функций проекта."""
    enable_utf8_output()
    try:
        users = load_users()
        categories = load_categories()
        chores = load_chores()
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
