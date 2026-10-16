import pytest


pytestmark = [pytest.mark.negative, ]


@pytest.mark.api
def test_create_expense_without_api_key_returns_401(client, payload_factory):
    response = client.post(
        "/api/expenses",
        json=payload_factory(),
    )

    assert response.status_code == 401


@pytest.mark.api
def test_create_expense_with_invalid_api_key_returns_401(client, payload_factory):
    response = client.post(
        "/api/expenses",
        json=payload_factory(),
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401


@pytest.mark.api
def test_get_expenses_without_api_key_returns_401(client):
    response = client.get("/api/expenses")

    assert response.status_code == 401


@pytest.mark.api
def test_health_without_api_key_returns_200(client):
    """
    /health — публичный эндпоинт, должен работать без ключа.
    """

    response = client.get("/health")

    assert response.status_code == 200