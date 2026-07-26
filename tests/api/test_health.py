from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_endpoint():

    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert isinstance(data["db_row_counts"], dict)

    expected_tables = [
        "analysis",
        "balancesheet",
        "cashflow",
        "companies",
        "documents",
        "financial_ratios",
        "market_cap",
        "peer_groups",
        "profitandloss",
        "sectors",
    ]

    for table in expected_tables:
        assert table in data["db_row_counts"]
        assert data["db_row_counts"][table] >= 0

    assert isinstance(data["uptime_seconds"], (int, float))

    assert isinstance(data["version"], str)