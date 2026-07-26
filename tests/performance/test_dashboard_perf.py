import time

import pytest
import requests

TICKERS = [
    "TCS",
    "INFY",
    "RELIANCE",
    "HDFCBANK",
    "SUNPHARMA",
]

BASE_URL = "http://127.0.0.1:8000/api/v1/companies"


def test_dashboard_performance():

    times = []

    print("=" * 60)
    print("Dashboard Performance Test")
    print("=" * 60)

    for ticker in TICKERS:

        start = time.perf_counter()

        try:
            response = requests.get(
                f"{BASE_URL}/{ticker}",
                timeout=10,
            )
        except requests.RequestException as exc:
            pytest.fail(f"Request failed: {exc}")

        end = time.perf_counter()

        assert response.status_code == 200

        elapsed = end - start
        times.append(elapsed)

        print(f"{ticker:<12} {elapsed:.3f} sec")

        assert elapsed < 3

    print("=" * 60)
    print(f"Average : {sum(times) / len(times):.3f} sec")
    print(f"Fastest : {min(times):.3f} sec")
    print(f"Slowest : {max(times):.3f} sec")
    print("PASS")
    print("=" * 60)