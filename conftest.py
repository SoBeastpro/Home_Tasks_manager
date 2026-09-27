"""Настройки pytest: корень проекта добавляется в пути импорта.

Благодаря этому тесты из каталога tests могут импортировать модули
проекта по имени, например: from models.chores import add_chore.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
