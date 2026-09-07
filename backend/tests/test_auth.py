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


class TestAuthSignup:
    """Tests for POST /api/v1/auth/signup."""

    @pytest.mark.asyncio
    async def test_signup_success(self, client, mock_supabase):
        """Valid signup request should return 201 with user details."""
        from unittest.mock import MagicMock
        mock_user = MagicMock()
        mock_user.id = "user-uuid-123"
        mock_user.email = "newuser@example.com"
        mock_res = MagicMock()
        mock_res.user = mock_user

        mock_supabase.auth.admin.create_user.return_value = mock_res

        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "Password123!",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["id"] == "user-uuid-123"
