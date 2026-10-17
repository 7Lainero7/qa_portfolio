import pytest


@pytest.mark.api
@pytest.mark.negative
@pytest.mark.parametrize(
    "missing_field",
    ["title", "amount_cents"],
)
def test_missing_required_field_returns_422(
    client,
    auth_headers,
    payload_factory,
    missing_field,
):
    payload = payload_factory()
    payload.pop(missing_field)

    response = client.post(
        "/api/expenses",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 422

@pytest.mark.api
@pytest.mark.negative
def test_invalid_amount_type_returns_422(client, auth_headers, payload_factory):
    payload = payload_factory(amount_cents="not-a-number")

    response = client.post(
        "/api/expenses",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.api
@pytest.mark.boundary
@pytest.mark.parametrize(
    "title",
    [
        "a",
        "a" * 50,
    ],
)
def test_title_valid_boundaries(client, auth_headers, payload_factory, title):
    response = client.post(
        "/api/expenses",
        json=payload_factory(title=title),
        headers=auth_headers,
    )

    assert response.status_code == 201


@pytest.mark.api
@pytest.mark.boundary
@pytest.mark.parametrize(
    "title",
    [
        "",
        "a" * 51,
    ],
)
def test_title_invalid_boundaries(client, auth_headers, payload_factory, title):
    response = client.post(
        "/api/expenses",
        json=payload_factory(title=title),
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.api
@pytest.mark.boundary
@pytest.mark.parametrize(
    "amount_cents",
    [
        1,
        100_000_000,
    ],
)
def test_amount_valid_boundaries(
    client,
    auth_headers,
    payload_factory,
    amount_cents,
):
    response = client.post(
        "/api/expenses",
        json=payload_factory(amount_cents=amount_cents),
        headers=auth_headers,
    )

    assert response.status_code == 201


@pytest.mark.api
@pytest.mark.boundary
@pytest.mark.parametrize(
    "amount_cents",
    [
        0,
        -1,
        100_000_001,
    ],
)
def test_amount_invalid_boundaries(
    client,
    auth_headers,
    payload_factory,
    amount_cents,
):
    response = client.post(
        "/api/expenses",
        json=payload_factory(amount_cents=amount_cents),
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.api
@pytest.mark.negative
def test_patch_with_null_category_returns_422(client, auth_headers, payload_factory):
    """
    Регрессионный тест для BUG-001.
    Проверяем, что явная передача null в category при PATCH возвращает 422, 
    а не вызывает IntegrityError (500).
    """
    # 1. Создаем расход
    create_response = client.post(
        "/api/expenses", 
        json=payload_factory(category="food"), 
        headers=auth_headers
    )
    expense_id = create_response.json()["id"]

    # 2. Пытаемся обновить category на null
    response = client.patch(
        f"/api/expenses/{expense_id}",
        json={"category": None},
        headers=auth_headers,
    )

    # 3. Проверяем, что получили валидационную ошибку, а не 500
    assert response.status_code == 422
    
    # Опционально: проверяем текст ошибки
    details = response.json()["detail"]
    assert any("category cannot be null" in str(err.get("msg", "")).lower() for err in details)
