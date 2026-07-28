import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.append(str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    assert response.json()["status"] == "running"


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["database"] == "connected"


def test_companies():

    response = client.get("/companies")

    assert response.status_code == 200

    assert isinstance(response.json(), list)

    assert len(response.json()) > 0


def test_company():

    response = client.get("/company/ABB")

    assert response.status_code == 200

    assert response.json()["id"] == "ABB"


def test_company_not_found():

    response = client.get("/company/XYZ123")

    assert response.status_code == 404


def test_financial_ratios():

    response = client.get("/financial-ratios/ABB")

    assert response.status_code == 200

    assert isinstance(response.json(), list)


def test_clusters():

    response = client.get("/clusters")

    assert response.status_code == 200

    assert isinstance(response.json(), list)


def test_cluster_summary():

    response = client.get("/cluster-summary")

    assert response.status_code == 200

    assert isinstance(response.json(), list)
