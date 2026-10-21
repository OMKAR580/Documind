from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "health_url" in data
    assert data["name"] == "DocuMind API"


def test_liveness_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "DocuMind API"
    assert "timestamp" in data


def test_liveness_probe(client: TestClient):
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_readiness_endpoint_healthy(client: TestClient, monkeypatch):
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
    assert data["components"]["database"]["details"] == "PostgreSQL reachable"


def test_readiness_endpoint_unhealthy_does_not_leak_secrets(client: TestClient, monkeypatch):
    # Mock database check to simulate connection failure with sensitive connection string in raw error
    raw_sensitive_error = (
        "Connection to postgres://admin:super_secret@private-db.internal:5432 failed"
    )
    monkeypatch.setattr(
        "app.api.v1.routes.health.check_database_connection",
        lambda: (False, raw_sensitive_error),
    )
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["components"]["database"]["status"] == "unhealthy"
    # Ensure sensitive credentials or raw details are never leaked to client
    assert "super_secret" not in response.text
    assert "private-db.internal" not in response.text
    assert data["components"]["database"]["details"] == "PostgreSQL connection unavailable"
