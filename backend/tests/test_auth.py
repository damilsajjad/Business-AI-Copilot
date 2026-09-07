"""Tests for authentication endpoints."""

import pytest

from tests.conftest import TEST_USER_EMAIL, TEST_USER_ID


class TestAuthMe:
    """Tests for GET /api/v1/auth/me."""

    @pytest.mark.asyncio
    async def test_returns_401_without_token(self, client):
        """Unauthenticated request should return 401."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_401_with_invalid_header(self, client):
        """Malformed authorization header should return 401."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "InvalidFormat"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_401_with_bad_token(self, client):
        """Invalid JWT token should return 401."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_user_info_when_authenticated(self, authenticated_client):
        """Authenticated request should return user info."""
        response = await authenticated_client.get("/api/v1/auth/me")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == TEST_USER_ID
        assert data["email"] == TEST_USER_EMAIL
        assert data["role"] == "authenticated"


class TestAuthProfile:
    """Tests for GET /api/v1/auth/profile."""

    @pytest.mark.asyncio
    async def test_returns_401_without_token(self, client):
        """Unauthenticated request should return 401."""
        response = await client.get("/api/v1/auth/profile")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_profile_when_authenticated(
        self, authenticated_client, mock_supabase
    ):
        """Authenticated request should return full profile from database."""
        # Configure mock to return profile data
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "id": TEST_USER_ID,
            "email": TEST_USER_EMAIL,
            "full_name": "Test User",
            "avatar_url": "",
        }

        response = await authenticated_client.get("/api/v1/auth/profile")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == TEST_USER_ID
        assert data["email"] == TEST_USER_EMAIL
        assert data["full_name"] == "Test User"
