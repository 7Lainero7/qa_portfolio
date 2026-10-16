import pytest


@pytest.mark.api
@pytest.mark.smoke
def test_create_expense_returns_201(client, auth_headers, payload_factory):
    payload = payload_factory(
        title="Coffee",
        amount_cents=35000,
    )

    response = client.post(
        "/api/expenses",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["id"] >= 1
    assert body["title"] == payload["title"]
    assert body["amount_cents"] == payload["amount_cents"]
    assert body["category"] == payload["category"]
    assert "created_at" in body


@pytest.mark.api
@pytest.mark.smoke
def test_create_expense_without_category_uses_default(
    client,
    auth_headers,
    payload_factory,
):
    payload = payload_factory()
    payload.pop("category", None)

    response = client.post(
        "/api/expenses",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["category"] == "other"


@pytest.mark.api
@pytest.mark.smoke
def test_get_created_expense(client, auth_headers, payload_factory):
    payload = payload_factory(title="Taxi")

    create_response = client.post(
        "/api/expenses",
        json=payload,
        headers=auth_headers,
    )

    expense_id = create_response.json()["id"]

    response = client.get(
        f"/api/expenses/{expense_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == expense_id
    assert response.json()["title"] == "Taxi"


@pytest.mark.api
@pytest.mark.smoke
def test_list_expenses_contains_created_item(
    client,
    auth_headers,
    payload_factory,
):
    payload = payload_factory(title="Groceries")

    client.post(
        "/api/expenses",
        json=payload,
        headers=auth_headers,
    )

    response = client.get(
        "/api/expenses",
        headers=auth_headers,
    )

    assert response.status_code == 200

    titles = [item["title"] for item in response.json()]

    assert "Groceries" in titles


@pytest.mark.api
@pytest.mark.negative
def test_get_missing_expense_returns_404(client, auth_headers):
    response = client.get(
        "/api/expenses/999999",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"


@pytest.mark.api
@pytest.mark.negative
def test_patch_missing_expense_returns_404(client, auth_headers):
    response = client.patch(
        "/api/expenses/999999",
        json={"title": "New title"},
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.api
@pytest.mark.negative
def test_delete_missing_expense_returns_404(client, auth_headers):
    response = client.delete(
        "/api/expenses/999999",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.api
@pytest.mark.smoke
def test_update_expense(client, auth_headers, payload_factory):
    payload = payload_factory(title="Old", amount_cents=1000)

    create_response = client.post(
        "/api/expenses",
        json=payload,
        headers=auth_headers,
    )

    expense_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/expenses/{expense_id}",
        json={"title": "New", "amount_cents": 2000},
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "New"
    assert update_response.json()["amount_cents"] == 2000


@pytest.mark.api
@pytest.mark.smoke
def test_delete_expense(client, auth_headers, payload_factory):
    payload = payload_factory(title="To delete")

    create_response = client.post(
        "/api/expenses",
        json=payload,
        headers=auth_headers,
    )

    expense_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/expenses/{expense_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/expenses/{expense_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404


@pytest.mark.api
def test_patch_with_empty_body_returns_200_no_op(client, auth_headers, payload_factory):
    create_response = client.post("/api/expenses", json=payload_factory(), headers=auth_headers)
    expense_id = create_response.json()["id"]

    # Пустой PATCH должен вернуть 200 и не изменить данные
    response = client.patch(f"/api/expenses/{expense_id}", json={}, headers=auth_headers)
    assert response.status_code == 200
    
    # Проверяем, что данные не изменились
    get_response = client.get(f"/api/expenses/{expense_id}", headers=auth_headers)
    assert get_response.json()["title"] == "Coffee"
