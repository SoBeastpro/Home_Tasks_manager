-- ==========================================
-- Home Tasks: SQL-запросы предметной области
-- ==========================================

-- 1. Выборка: список всех дел
SELECT
    id,
    title,
    due_date,
    status,
    priority
FROM chores
ORDER BY due_date, priority DESC;

-- 2. Выборка: список категорий
SELECT
    id,
    name
FROM categories
ORDER BY name;

-- 3. Фильтрация WHERE: дела с высоким приоритетом
SELECT
    id,
    title,
    priority,
    status
FROM chores
WHERE priority >= 3
ORDER BY priority DESC, due_date;

-- 4. Фильтрация WHERE: невыполненные дела
SELECT
    id,
    title,
    due_date,
    status
FROM chores
WHERE status != 'Выполнено'
ORDER BY due_date;

-- 5. Фильтрация WHERE: дела на выбранную дату
SELECT
    id,
    title,
    due_date,
    status
FROM chores
WHERE due_date = '2026-09-21'
ORDER BY priority DESC;

-- 6. JOIN: дело вместе с исполнителем и категорией
SELECT
    chores.id,
    chores.title,
    chores.due_date,
    chores.status,
    chores.priority,
    users.name AS user_name,
    users.email AS user_email,
    categories.name AS category_name
FROM chores
JOIN users
    ON chores.user_id = users.id
JOIN categories
    ON chores.category_id = categories.id
ORDER BY chores.due_date;

-- 7. JOIN: невыполненные дела со связанными объектами
SELECT
    chores.id,
    chores.title,
    chores.due_date,
    chores.status,
    users.name AS user_name,
    categories.name AS category_name
FROM chores
JOIN users
    ON chores.user_id = users.id
JOIN categories
    ON chores.category_id = categories.id
WHERE chores.status != 'Выполнено'
ORDER BY chores.due_date;

-- 8. Агрегат: общее количество дел
SELECT
    COUNT(*) AS chores_count
FROM chores;

-- 9. Агрегат: количество невыполненных дел
SELECT
    COUNT(*) AS open_chores_count
FROM chores
WHERE status != 'Выполнено';

-- 10. GROUP BY: количество дел в каждой категории
SELECT
    categories.name AS category_name,
    COUNT(chores.id) AS chores_count
FROM categories
LEFT JOIN chores
    ON categories.id = chores.category_id
GROUP BY categories.id, categories.name
ORDER BY chores_count DESC;

-- 11. GROUP BY: количество дел у каждого исполнителя
SELECT
    users.name AS user_name,
    COUNT(chores.id) AS chores_count
FROM users
LEFT JOIN chores
    ON users.id = chores.user_id
GROUP BY users.id, users.name
ORDER BY chores_count DESC;

-- 12. GROUP BY: количество дел по статусам
SELECT
    status,
    COUNT(*) AS chores_count
FROM chores
GROUP BY status
ORDER BY chores_count DESC;

-- 13. HAVING: категории, в которых больше одного дела
SELECT
    categories.name AS category_name,
    COUNT(chores.id) AS chores_count
FROM categories
JOIN chores
    ON categories.id = chores.category_id
GROUP BY categories.id, categories.name
HAVING COUNT(chores.id) > 1
ORDER BY chores_count DESC;

-- 14. LIMIT и OFFSET: ближайшие дела
SELECT
    id,
    title,
    due_date
FROM chores
ORDER BY due_date
LIMIT 3 OFFSET 0;
