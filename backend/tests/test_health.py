"""Tests for the health endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_200(client):
    """GET /api/v1/health should return 200 with status healthy."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_health_contains_version(client):
    """Health response should include the application version."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_returns_json(client):
    """Health endpoint should return application/json content type."""
    response = await client.get("/api/v1/health")
    assert response.headers["content-type"] == "application/json"
