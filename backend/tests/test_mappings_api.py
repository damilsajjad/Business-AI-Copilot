"""Tests for data mapping API endpoints."""

from uuid import uuid4

import pytest

from app.data.synthetic_data import generate_retail_dataset
from app.services.profiler import profile_dataset
from tests.conftest import TEST_BUSINESS_ID

TEST_FILE_ID = str(uuid4())

# Profile metadata for mocking
_df = generate_retail_dataset(num_orders=20)
_profile = profile_dataset(file_id=TEST_FILE_ID, file_name="sales.csv", sheets_dict={"Sheet1": _df})
TEST_FILE_WITH_PROFILE = {
    "id": TEST_FILE_ID,
    "business_id": TEST_BUSINESS_ID,
    "metadata": _profile.model_dump(),
}

TEST_MAPPING_RECORD = {
    "id": str(uuid4()),
    "business_id": TEST_BUSINESS_ID,
    "file_id": TEST_FILE_ID,
    "mappings": [
        {"target_field": "order_date", "source_sheet": "Sheet1", "source_column": "order_date", "confidence": 1.0, "reasoning": ""},
        {"target_field": "total_revenue", "source_sheet": "Sheet1", "source_column": "total_revenue", "confidence": 1.0, "reasoning": ""},
    ],
    "status": "confirmed",
    "created_at": "2025-01-01T00:00:00+00:00",
    "updated_at": "2025-01-01T00:00:00+00:00",
}


@pytest.mark.asyncio
async def test_get_canonical_schema(client):
    """GET /api/v1/canonical-schema should return the standard canonical fields."""
    response = await client.get("/api/v1/canonical-schema")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    field_names = [f["name"] for f in data]
    assert "order_date" in field_names
    assert "total_revenue" in field_names


class TestProposeMappingAPI:
    """Tests for POST /api/v1/businesses/{business_id}/uploads/{file_id}/mapping/propose."""

    @pytest.mark.asyncio
    async def test_returns_401_without_token(self, client):
        """Unauthenticated propose request should return 401."""
        response = await client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/mapping/propose"
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_propose_mapping_success(self, authenticated_client, mock_supabase):
        """Authenticated request should return AI proposed mappings."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = (
            TEST_FILE_WITH_PROFILE
        )

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/mapping/propose"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["file_id"] == TEST_FILE_ID
        assert len(data["mappings"]) > 0


class TestConfirmMappingAPI:
    """Tests for POST /api/v1/businesses/{business_id}/uploads/{file_id}/mapping/confirm."""

    @pytest.mark.asyncio
    async def test_confirm_invalid_mapping_returns_400(
        self, authenticated_client, mock_supabase
    ):
        """Confirming an invalid mapping missing required fields should return 400."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = (
            TEST_FILE_WITH_PROFILE
        )

        # Missing order_date
        invalid_payload = {
            "mappings": [
                {"target_field": "total_revenue", "source_sheet": "Sheet1", "source_column": "total_revenue", "confidence": 1.0, "reasoning": ""}
            ]
        }

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/mapping/confirm",
            json=invalid_payload,
        )
        assert response.status_code == 400
        assert "Missing required field" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_confirm_valid_mapping_success(
        self, authenticated_client, mock_supabase
    ):
        """Confirming a valid mapping should save and return 201."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = (
            TEST_FILE_WITH_PROFILE
        )
        mock_supabase.table.return_value.upsert.return_value.execute.return_value.data = [
            TEST_MAPPING_RECORD
        ]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": TEST_FILE_ID, "status": "mapped"}
        ]

        valid_payload = {
            "mappings": [
                {"target_field": "order_date", "source_sheet": "Sheet1", "source_column": "order_date", "confidence": 1.0, "reasoning": ""},
                {"target_field": "total_revenue", "source_sheet": "Sheet1", "source_column": "total_revenue", "confidence": 1.0, "reasoning": ""},
            ]
        }

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/mapping/confirm",
            json=valid_payload,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["file_id"] == TEST_FILE_ID
        assert data["status"] == "confirmed"


class TestGetConfirmedMappingAPI:
    """Tests for GET /api/v1/businesses/{business_id}/uploads/{file_id}/mapping."""

    @pytest.mark.asyncio
    async def test_get_existing_mapping(self, authenticated_client, mock_supabase):
        """Should retrieve the confirmed mapping."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = (
            TEST_MAPPING_RECORD
        )

        response = await authenticated_client.get(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/mapping"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["file_id"] == TEST_FILE_ID
        assert len(data["mappings"]) == 2
