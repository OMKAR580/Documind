from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "health_url" in data
    assert data["name"] == "DocuMind API"


def test_liveness_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "DocuMind API"
    assert "timestamp" in data


def test_liveness_probe():
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_readiness_endpoint_healthy(monkeypatch):
    # Mock database check to return success
    monkeypatch.setattr(
        "app.api.v1.routes.health.check_database_connection",
        lambda: (True, None),
    )
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["components"]["database"]["status"] == "healthy"


def test_readiness_endpoint_unhealthy(monkeypatch):
    # Mock database check to simulate connection failure
    monkeypatch.setattr(
        "app.api.v1.routes.health.check_database_connection",
        lambda: (False, "Connection refused: database server down"),
    )
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["components"]["database"]["status"] == "unhealthy"
    assert "database server down" in data["components"]["database"]["details"]
