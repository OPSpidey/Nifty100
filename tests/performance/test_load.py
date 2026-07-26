import threading
import time

import pytest
import requests

URL = "http://127.0.0.1:8000/api/v1/screener?min_roe=15"

times = []


def worker():

    start = time.perf_counter()

    try:
        response = requests.get(URL, timeout=10)
    except requests.RequestException as exc:
        pytest.fail(f"Request failed: {exc}")

    end = time.perf_counter()

    assert response.status_code == 200

    times.append(end - start)


def test_load():

    times.clear()
    threads = []
    overall_start = time.perf_counter()

    for _ in range(10):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    overall_end = time.perf_counter()

    print()

    print("=" * 50)
    print("Load Test Completed")
    print("=" * 50)
    print(f"Completed Requests : {len(times)}")
    print(f"Total Time         : {overall_end - overall_start:.3f} sec")
    if not times:
        pytest.fail("No requests completed successfully.")

    print(f"Average Time       : {sum(times)/len(times):.3f} sec")
    print(f"Fastest Request    : {min(times):.3f} sec")
    print(f"Slowest Request    : {max(times):.3f} sec")
    print("=" * 50)

    assert len(times) == 10
    assert overall_end - overall_start < 10

    print("PASS: 10 concurrent requests completed within 10 seconds.")