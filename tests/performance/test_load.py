import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import threading
import time

from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)

NUM_REQUESTS = 10
times = []


def hit_api():
    start = time.perf_counter()

    response = client.get("/screener")

    end = time.perf_counter()

    assert response.status_code == 200
    times.append(end - start)


threads = []

overall_start = time.perf_counter()

for _ in range(NUM_REQUESTS):
    t = threading.Thread(target=hit_api)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

overall_end = time.perf_counter()

print("=" * 50)
print(f"Concurrent Requests : {NUM_REQUESTS}")
print(f"Total Time          : {overall_end-overall_start:.3f} sec")
print(f"Average Response    : {sum(times)/len(times):.3f} sec")
print(f"Fastest             : {min(times):.3f} sec")
print(f"Slowest             : {max(times):.3f} sec")
print("=" * 50)

assert overall_end - overall_start < 10

print("\n✅ Load Test PASSED")
