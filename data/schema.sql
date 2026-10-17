-- Очищаем таблицы, если они есть (для идемпотентности)
DROP TABLE IF EXISTS mart_expenses_by_category;
DROP TABLE IF EXISTS staging_expenses;

-- 1. Staging: сырые данные
-- ДОБАВЛЕНО: CHECK (amount_cents > 0) для защиты на уровне БД
CREATE TABLE staging_expenses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    amount_cents BIGINT CHECK (amount_cents > 0),
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Mart: витрина данных (агрегация по категориям)
CREATE TABLE mart_expenses_by_category (
    category VARCHAR(50) PRIMARY KEY,
    total_amount_cents BIGINT,
    expense_count INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);