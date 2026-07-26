from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_get_all_sectors():

    response = client.get("/api/v1/sectors")

    assert response.status_code == 200

    sectors = response.json()

    assert isinstance(sectors, list)

    assert len(sectors) == 10


def test_it_sector():

    response = client.get(
        "/api/v1/sectors/Information Technology/companies"
    )

    assert response.status_code == 200

    companies = response.json()

    assert isinstance(companies, list)

    assert len(companies) > 0

    for company in companies:
        assert "id" in company
        assert "company_name" in company
        assert "net_profit_margin_pct" in company


def test_invalid_sector():

    response = client.get(
        "/api/v1/sectors/INVALID/companies"
    )

    assert response.status_code == 404