"""Shared test fixtures."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.auth import get_current_user
from app.core.supabase import get_supabase_client
from app.main import app

# --- Test user data ---
TEST_USER_ID = str(uuid4())
TEST_USER_EMAIL = "test@example.com"
TEST_USER = {
    "id": TEST_USER_ID,
    "email": TEST_USER_EMAIL,
    "role": "authenticated",
}

TEST_BUSINESS_ID = str(uuid4())
TEST_BUSINESS = {
    "id": TEST_BUSINESS_ID,
    "name": "Test Business",
    "industry": "Retail",
    "description": "A test business",
    "created_at": "2025-01-01T00:00:00+00:00",
    "updated_at": "2025-01-01T00:00:00+00:00",
}

TEST_MEMBERSHIP = {
    "id": str(uuid4()),
    "business_id": TEST_BUSINESS_ID,
    "user_id": TEST_USER_ID,
    "role": "owner",
    "created_at": "2025-01-01T00:00:00+00:00",
}


@pytest.fixture
async def client():
    """Async HTTP client wired to the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def authenticated_client():
    """Async HTTP client with authentication bypassed.

    Overrides the get_current_user dependency to return a test user
    without requiring a real JWT token.
    """

    async def _mock_current_user():
        return TEST_USER

    app.dependency_overrides[get_current_user] = _mock_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up dependency override
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def mock_supabase():
    """Mock the Supabase client for database operations.

    Patches get_supabase_client everywhere it is imported so that
    no real Supabase credentials are required. Returns the MagicMock
    client that can be configured per-test.
    """
    mock_client = MagicMock()

    # Clear the lru_cache to ensure our mock is used
    get_supabase_client.cache_clear()

    # Patch in every module that imports get_supabase_client
    with (
        patch(
            "app.api.v1.auth.get_supabase_client", return_value=mock_client
        ),
        patch(
            "app.api.v1.businesses.get_supabase_client", return_value=mock_client
        ),
        patch(
            "app.api.v1.uploads.get_supabase_client", return_value=mock_client
        ),
        patch(
            "app.api.v1.mappings.get_supabase_client", return_value=mock_client
        ),
        patch(
            "app.api.v1.analytics.get_supabase_client", return_value=mock_client
        ),
        patch(
            "app.api.v1.ml.get_supabase_client", return_value=mock_client
        ),
        patch(
            "app.api.v1.agents.get_supabase_client", return_value=mock_client
        ),
        patch(
            "app.api.v1.actions.get_supabase_client", return_value=mock_client
        ),
        patch(
            "app.api.v1.reports.get_supabase_client", return_value=mock_client
        ),
        patch(
            "app.core.auth.get_supabase_client", return_value=mock_client
        ),
    ):
        yield mock_client

    get_supabase_client.cache_clear()
