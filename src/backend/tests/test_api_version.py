"""Tests for versioned API routes."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    return TestClient(app)


def test_health_includes_api_version(client):
    for path in ("/api/health", "/api/v1/health"):
        res = client.get(path)
        assert res.status_code == 200
        body = res.json()
        assert body["api_version"] == "1.1.0"
        assert body["active_model_version"] == "1.0.0"


def test_version_endpoint(client):
    res = client.get("/api/v1/version")
    assert res.status_code == 200
    body = res.json()
    assert body["api_version"] == "1.1.0"
    assert body["preferred_prefix"] == "/api/v1"
    assert body["active_model"]["version"] == "1.0.0"


def test_legacy_api_alias(client):
    res = client.get("/api/models")
    assert res.status_code == 200
    assert res.json()["api_version"] == "1.1.0"
