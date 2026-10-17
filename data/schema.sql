-- Очищаем таблицы, если они есть (для идемпотентности)
DROP TABLE IF EXISTS mart_expenses_by_category;
DROP TABLE IF EXISTS staging_expenses;

-- 1. Staging: сырые данные
-- ДОБАВЛЕНО: CHECK (amount_cents > 0) для защиты на уровне БД
-- ВАЖНО: лимиты длины и множество категорий должны совпадать с
-- backend/app/models.py (expenses: title VARCHAR(50), category VARCHAR(30)).
-- Расхождение схем означает, что staging принимает данные, которые
-- продуктовая таблицане приняла бы, — качество данных проверялось не на тех контрактах.
CREATE TABLE staging_expenses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    amount_cents BIGINT NOT NULL CHECK (amount_cents > 0),
    category VARCHAR(30) NOT NULL DEFAULT 'other'
        CHECK (category IN ('food', 'transport', 'entertainment', 'utilities', 'other')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Mart: витрина данных (агрегация по категориям)
CREATE TABLE mart_expenses_by_category (
    category VARCHAR(30) PRIMARY KEY
        CHECK (category IN ('food', 'transport', 'entertainment', 'utilities', 'other')),
    total_amount_cents BIGINT NOT NULL CHECK (total_amount_cents >= 0),
    expense_count INT NOT NULL CHECK (expense_count >= 0),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);