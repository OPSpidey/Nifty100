from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_get_all_companies():

    response = client.get("/api/v1/companies")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert len(data) > 0


def test_get_tcs():

    response = client.get("/api/v1/companies/TCS")

    assert response.status_code == 200

    company = response.json()

    assert company["company_id"] == "TCS"
    assert company["company_name"] == "Tata Consultancy Services Ltd"
    assert company["broad_sector"] == "Information Technology"

    assert "return_on_equity_pct" in company
    assert company["return_on_equity_pct"] is not None
    assert company["roce_pct"] is not None
    assert "roce_pct" in company
    assert "net_profit_margin_pct" in company

def test_invalid_company():

    response = client.get("/api/v1/companies/INVALID")

    assert response.status_code == 404