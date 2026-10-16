import pytest

pytestmark = pytest.mark.data_qa


def test_no_nulls_in_mart_keys(db_conn):
    """В витрине не должно быть NULL в первичном ключе (категории)."""
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM mart_expenses_by_category WHERE category IS NULL;")
        null_count = cur.fetchone()[0]
        assert null_count == 0, "Найдены записи с NULL в категории в витрине"


def test_no_negative_amounts_in_staging(db_conn):
    """В сырых данных не должно быть отрицательных сумм."""
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM staging_expenses WHERE amount_cents < 0;")
        negative_count = cur.fetchone()[0]
        assert negative_count == 0, "Найдены отрицательные суммы в staging"


def test_row_counts_match_aggregation(db_conn):
    """Общее количество записей в staging должно равняться сумме expense_count в mart."""
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM staging_expenses;")
        staging_total = cur.fetchone()[0]
        
        cur.execute("SELECT SUM(expense_count) FROM mart_expenses_by_category;")
        mart_total = cur.fetchone()[0]
        
        assert staging_total == mart_total, f"Несовпадение количества: staging={staging_total}, mart={mart_total}"


def test_amounts_reconcile(db_conn):
    """Сумма всех amount_cents в staging должна быть равна сумме total_amount_cents в mart."""
    with db_conn.cursor() as cur:
        cur.execute("SELECT SUM(amount_cents) FROM staging_expenses;")
        staging_sum = cur.fetchone()[0] or 0
        
        cur.execute("SELECT SUM(total_amount_cents) FROM mart_expenses_by_category;")
        mart_sum = cur.fetchone()[0] or 0
        
        assert staging_sum == mart_sum, f"Несовпадение сумм: staging={staging_sum}, mart={mart_sum}"


def test_no_orphan_categories(db_conn):
    """Каждая категория в mart должна существовать в staging."""
    with db_conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM mart_expenses_by_category m
            WHERE NOT EXISTS (
                SELECT 1 FROM staging_expenses s WHERE s.category = m.category
            );
        """)
        orphan_count = cur.fetchone()[0]
        assert orphan_count == 0, "Найдены категории в mart, которых нет в staging"


def test_data_qa_catches_negative_amounts(db_conn):
    """
    Мутационный тест: намеренно вставляем 'грязные' данные и проверяем, 
    что тест качества данных их обнаруживает.
    """
    with db_conn.cursor() as cur:
        # 1. Намеренно ломаем данные (обходим логику генератора)
        cur.execute("INSERT INTO staging_expenses (title, amount_cents, category) VALUES ('Bad Data', -500, 'food');")
        db_conn.commit()
        
        # 2. Проверяем, что наш тест качества это ловит
        cur.execute("SELECT COUNT(*) FROM staging_expenses WHERE amount_cents < 0;")
        negative_count = cur.fetchone()[0]
        
        # Мы ОЖИДАЕМ, что найдется хотя бы 1 отрицательная запись, 
        # тем самым доказывая, что тест НЕ является тавтологией.
        assert negative_count >= 1, "Тест не смог обнаружить намеренно вставленные отрицательные значения"
        
        # 3. Откатываем изменения, чтобы не ломать другие тесты
        db_conn.rollback()
