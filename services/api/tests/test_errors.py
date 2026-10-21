from fastapi import APIRouter
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.exceptions import AppException, NotFoundException
from app.main import app

# Auxiliary router for verifying custom exception handlers
dummy_error_router = APIRouter()


class SamplePayload(BaseModel):
    name: str
    count: int


@dummy_error_router.post("/test/validation")
async def trigger_validation(payload: SamplePayload):
    return payload


@dummy_error_router.get("/test/custom-not-found")
async def trigger_custom_not_found():
    raise NotFoundException("Custom item not found", details={"item_id": 42})


@dummy_error_router.get("/test/custom-app-exception")
async def trigger_custom_app_exception():
    raise AppException("Custom domain failure", code="DOMAIN_ERROR", status_code=400)


@dummy_error_router.get("/test/unhandled")
async def trigger_unhandled():
    raise RuntimeError("Unexpected internal crash")


app.include_router(dummy_error_router)


def test_404_error_envelope(client: TestClient):
    response = client.get("/api/v1/non-existent-route-404")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "Not Found" in data["error"]["message"]


def test_422_validation_error_envelope(client: TestClient):
    # Missing required 'count' field
    response = client.post("/test/validation", json={"name": "test"})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Request validation failed"
    assert isinstance(data["error"]["details"], list)


def test_custom_app_exception_envelope(client: TestClient):
    response = client.get("/test/custom-app-exception")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "DOMAIN_ERROR"
    assert data["error"]["message"] == "Custom domain failure"


def test_custom_not_found_envelope(client: TestClient):
    response = client.get("/test/custom-not-found")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert data["error"]["message"] == "Custom item not found"
    assert data["error"]["details"] == {"item_id": 42}


def test_unhandled_500_exception_envelope():
    client_no_raise = TestClient(app, raise_server_exceptions=False)
    response = client_no_raise.get("/test/unhandled")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert "internal error occurred" in data["error"]["message"]
    # Ensure stack trace or raw exception details are NOT exposed
    assert "RuntimeError" not in response.text
    assert "Unexpected internal crash" not in response.text
