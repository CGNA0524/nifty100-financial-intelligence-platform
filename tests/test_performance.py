import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


def test_companies_response_time():

    start = time.perf_counter()

    response = client.get("/companies")

    end = time.perf_counter()

    assert response.status_code == 200

    assert (end - start) < 1.0


def test_health_response_time():

    start = time.perf_counter()

    response = client.get("/health")

    end = time.perf_counter()

    assert response.status_code == 200

    assert (end - start) < 0.5


def test_clusters_response_time():

    start = time.perf_counter()

    response = client.get("/clusters")

    end = time.perf_counter()

    assert response.status_code == 200

    assert (end - start) < 1.0
