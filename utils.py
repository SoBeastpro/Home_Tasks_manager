"""Вспомогательные функции проекта: работа с датами и безопасный ввод.

Функции ввода не завершают программу при ошибке: некорректное значение
перехватывается исключением, после чего запрос повторяется.
"""

import sys
from datetime import date, datetime

INPUT_DATE_FORMAT = "%d.%m.%Y"
STORAGE_DATE_FORMAT = "%Y-%m-%d"
DATE_FORMATS: tuple[str, ...] = (INPUT_DATE_FORMAT, STORAGE_DATE_FORMAT)


def enable_utf8_output() -> None:
    """Перевести вывод программы в кодировку UTF-8.

    Нужно для корректного отображения русского текста в консоли Windows.
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass


def parse_date(value: str | date) -> date:
    """Преобразовать строку в дату.

    Поддерживаются форматы ДД.ММ.ГГГГ и ГГГГ-ММ-ДД.
    Вызывает ValueError, если строка не является датой.
    """
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            continue
    raise ValueError(f"Некорректная дата: «{value}»")


def format_date(value: str | date) -> str:
    """Вернуть дату в виде строки формата ДД.ММ.ГГГГ."""
    return parse_date(value).strftime(INPUT_DATE_FORMAT)


def date_to_storage(value: str | date) -> str:
    """Вернуть дату в виде строки для хранения в JSON-файле."""
    return parse_date(value).strftime(STORAGE_DATE_FORMAT)


def input_text(prompt: str) -> str:
    """Запросить у пользователя непустую строку."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("Значение не может быть пустым, повторите ввод.")


def input_int(
    prompt: str,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Запросить у пользователя целое число из заданного диапазона."""
    while True:
        try:
            number = int(input(prompt).strip())
        except ValueError:
            print("Нужно ввести целое число, повторите ввод.")
            continue
        if min_value is not None and number < min_value:
            print(f"Значение не может быть меньше {min_value}.")
            continue
        if max_value is not None and number > max_value:
            print(f"Значение не может быть больше {max_value}.")
            continue
        return number


def input_date(prompt: str) -> date:
    """Запросить у пользователя дату в формате ДД.ММ.ГГГГ."""
    while True:
        try:
            return parse_date(input(prompt))
        except ValueError as error:
            print(f"{error}. Ожидается формат ДД.ММ.ГГГГ, повторите ввод.")
