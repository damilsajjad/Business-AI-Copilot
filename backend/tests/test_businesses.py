"""Tests for business CRUD endpoints."""


import pytest

from tests.conftest import (
    TEST_BUSINESS,
    TEST_BUSINESS_ID,
)


class TestCreateBusiness:
    """Tests for POST /api/v1/businesses."""

    @pytest.mark.asyncio
    async def test_returns_401_without_token(self, client):
        """Unauthenticated request should return 401."""
        response = await client.post(
            "/api/v1/businesses",
            json={"name": "My Business"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_creates_business_with_owner_membership(
        self, authenticated_client, mock_supabase
    ):
        """Should create business and owner membership, returning 201."""
        # Mock business insert
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            TEST_BUSINESS
        ]

        response = await authenticated_client.post(
            "/api/v1/businesses",
            json={
                "name": "Test Business",
                "industry": "Retail",
                "description": "A test business",
            },
        )
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "Test Business"
        assert data["industry"] == "Retail"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_creates_business_with_defaults(
        self, authenticated_client, mock_supabase
    ):
        """Business should be created with default empty industry and description."""
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {
                **TEST_BUSINESS,
                "name": "Minimal Biz",
                "industry": "",
                "description": "",
            }
        ]

        response = await authenticated_client.post(
            "/api/v1/businesses",
            json={"name": "Minimal Biz"},
        )
        assert response.status_code == 201
        assert response.json()["industry"] == ""


class TestListBusinesses:
    """Tests for GET /api/v1/businesses."""

    @pytest.mark.asyncio
    async def test_returns_401_without_token(self, client):
        """Unauthenticated request should return 401."""
        response = await client.get("/api/v1/businesses")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_user_businesses(self, authenticated_client, mock_supabase):
        """Should return businesses the user is a member of."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "role": "owner",
                "businesses": TEST_BUSINESS,
            }
        ]

        response = await authenticated_client.get("/api/v1/businesses")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Business"
        assert data[0]["role"] == "owner"

    @pytest.mark.asyncio
    async def test_returns_empty_list_for_no_businesses(
        self, authenticated_client, mock_supabase
    ):
        """User with no businesses should get an empty list."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = (
            []
        )

        response = await authenticated_client.get("/api/v1/businesses")
        assert response.status_code == 200
        assert response.json() == []


class TestGetBusiness:
    """Tests for GET /api/v1/businesses/{business_id}."""

    @pytest.mark.asyncio
    async def test_returns_401_without_token(self, client):
        """Unauthenticated request should return 401."""
        response = await client.get(f"/api/v1/businesses/{TEST_BUSINESS_ID}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_403_for_non_member(self, authenticated_client, mock_supabase):
        """Non-member should get 403."""
        # Mock membership check returns empty
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = (
            []
        )

        response = await authenticated_client.get(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}"
        )
        assert response.status_code == 403


class TestUpdateBusiness:
    """Tests for PUT /api/v1/businesses/{business_id}."""

    @pytest.mark.asyncio
    async def test_returns_401_without_token(self, client):
        """Unauthenticated request should return 401."""
        response = await client.put(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}",
            json={"name": "Updated"},
        )
        assert response.status_code == 401


class TestDeleteBusiness:
    """Tests for DELETE /api/v1/businesses/{business_id}."""

    @pytest.mark.asyncio
    async def test_returns_401_without_token(self, client):
        """Unauthenticated request should return 401."""
        response = await client.delete(f"/api/v1/businesses/{TEST_BUSINESS_ID}")
        assert response.status_code == 401
