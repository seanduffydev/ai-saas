"""Tests for main app (root and health)."""

import pytest
from fastapi.testclient import TestClient


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Commodity Forecasting Lab API"
    assert data["status"] == "running"
    assert data["version"] == "1.0.0"
    assert data["docs"] == "/docs"


def test_health(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
