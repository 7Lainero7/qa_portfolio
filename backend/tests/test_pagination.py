import pytest


pytestmark = [pytest.mark.api, pytest.mark.boundary]


@pytest.fixture()
def create_10_expenses(client, auth_headers, payload_factory):
    """
    Создаёт 10 расходов с title "Expense 1".."Expense 10".
    
    Возвращает список созданных записей (ответы от API).
    """

    created = []
    
    for i in range(1, 11):
        response = client.post(
            "/api/expenses",
            json=payload_factory(
                title=f"Expense {i}",
                amount_cents=i * 1000,
            ),
            headers=auth_headers,
        )
        
        created.append(response.json())
    
    return created


def test_default_limit_returns_all_when_few_items(
    client,
    auth_headers,
    create_10_expenses,
):
    """
    По умолчанию limit=100, если записей меньше — вернутся все.
    """

    response = client.get("/api/expenses", headers=auth_headers)

    assert response.status_code == 200
    
    items = response.json()
    assert len(items) == 10
    
    # Проверяем, что вернулись именно созданные записи
    created_ids = {item["id"] for item in create_10_expenses}
    returned_ids = {item["id"] for item in items}
    
    assert created_ids == returned_ids


def test_limit_1_returns_one_item(
    client,
    auth_headers,
    create_10_expenses,
):
    """
    BVA: минимальный лимит = 1.
    """

    response = client.get(
        "/api/expenses?limit=1",
        headers=auth_headers,
    )

    assert response.status_code == 200
    
    items = response.json()
    assert len(items) == 1
    
    # Из-за сортировки desc первой будет последняя созданная запись
    assert items[0]["title"] == "Expense 10"
    assert items[0]["id"] == create_10_expenses[-1]["id"]


def test_limit_0_returns_422(
        client,
        auth_headers
):
    """
    BVA: лимит = 0 — невалидное значение.
    Запрос пустого списка не имеет практического смысла.
    """
    response = client.get("/api/expenses?limit=0", headers=auth_headers)
    assert response.status_code == 422


def test_limit_1000_is_maximum_valid_value(
    client,
    auth_headers,
    create_10_expenses,
):
    """
    BVA: максимальный лимит = 1000.
    """

    response = client.get(
        "/api/expenses?limit=1000",
        headers=auth_headers,
    )

    assert response.status_code == 200
    
    items = response.json()
    assert len(items) == 10
    
    # Проверяем, что все созданные записи вернулись
    created_ids = {item["id"] for item in create_10_expenses}
    returned_ids = {item["id"] for item in items}
    
    assert created_ids == returned_ids


def test_limit_1001_returns_422(
    client,
    auth_headers,
):
    """
    BVA: лимит > 1000 — невалидное значение, должно вернуть 422.
    
    Фикстура не нужна, потому что запрос не доходит до создания данных.
    """

    response = client.get(
        "/api/expenses?limit=1001",
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_limit_negative_returns_422(
    client,
    auth_headers,
):
    """
    BVA: отрицательный лимит — невалидное значение.
    
    Фикстура не нужна, потому что запрос не доходит до создания данных.
    """

    response = client.get(
        "/api/expenses?limit=-1",
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_offset_0_returns_from_beginning(
    client,
    auth_headers,
    create_10_expenses,
):
    """
    BVA: offset = 0 — начало списка.
    """

    response = client.get(
        "/api/expenses?offset=0&limit=5",
        headers=auth_headers,
    )

    assert response.status_code == 200
    
    items = response.json()
    assert len(items) == 5
    
    # Из-за сортировки desc offset=0 это последние 5 созданных записей
    assert items[0]["title"] == "Expense 10"
    assert items[1]["title"] == "Expense 9"
    assert items[2]["title"] == "Expense 8"
    assert items[3]["title"] == "Expense 7"
    assert items[4]["title"] == "Expense 6"


def test_offset_beyond_data_returns_empty(
    client,
    auth_headers,
    create_10_expenses,
):
    """
    BVA: offset за концом данных — пустой список.
    """

    response = client.get(
        "/api/expenses?offset=100",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_offset_negative_returns_422(
    client,
    auth_headers,
):
    """
    BVA: отрицательный offset — невалидное значение.
    
    Фикстура не нужна, потому что запрос не доходит до создания данных.
    """

    response = client.get(
        "/api/expenses?offset=-1",
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_items_sorted_by_id_desc(
    client,
    auth_headers,
    create_10_expenses,
):
    """
    Проверяем, что новые записи (с большим id) идут первыми.
    """

    response = client.get("/api/expenses", headers=auth_headers)

    assert response.status_code == 200

    items = response.json()
    ids = [item["id"] for item in items]

    assert ids == sorted(ids, reverse=True)

    # Первая запись должна быть "Expense 10", последняя — "Expense 1"
    assert items[0]["title"] == "Expense 10"
    assert items[-1]["title"] == "Expense 1"
    
    # Проверяем, что ID соответствуют созданным записям
    assert items[0]["id"] == create_10_expenses[-1]["id"]  # последняя созданная
    assert items[-1]["id"] == create_10_expenses[0]["id"]  # первая созданная


def test_pagination_with_limit_and_offset(
    client,
    auth_headers,
    create_10_expenses,
):
    """
    Комбинация limit + offset.
    Берём записи с 3 по 7 (offset=2, limit=5).
    """

    response = client.get(
        "/api/expenses?offset=2&limit=5",
        headers=auth_headers,
    )

    assert response.status_code == 200

    items = response.json()
    assert len(items) == 5

    # Из-за сортировки desc:
    # offset=0: Expense 10, 9, 8, 7, 6, 5, 4, 3, 2, 1
    # offset=2: Expense 8, 7, 6, 5, 4
    
    assert items[0]["title"] == "Expense 8"
    assert items[1]["title"] == "Expense 7"
    assert items[2]["title"] == "Expense 6"
    assert items[3]["title"] == "Expense 5"
    assert items[4]["title"] == "Expense 4"
    
    # Проверяем, что вернулись именно созданные записи
    returned_ids = {item["id"] for item in items}
    created_ids = {item["id"] for item in create_10_expenses}
    
    assert returned_ids.issubset(created_ids)