from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_screener_min_roe():

    response = client.get(
        "/api/v1/screener?min_roe=15"
    )

    assert response.status_code == 200

    companies = response.json()

    assert len(companies) > 0

    for company in companies:
        assert company["return_on_equity_pct"] >= 15


def test_invalid_min_roe():

    response = client.get(
        "/api/v1/screener?min_roe=-5"
    )

    assert response.status_code == 400


def test_sector_filter():

    response = client.get(
        "/api/v1/screener?sector=Financials"
    )

    assert response.status_code == 200

    companies = response.json()

    for company in companies:
        assert company["broad_sector"] == "Financials"