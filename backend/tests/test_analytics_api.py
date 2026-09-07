"""Tests for analytics API endpoints."""

from unittest.mock import patch
from uuid import uuid4

import pytest

from app.data.synthetic_data import generate_retail_dataset
from tests.conftest import TEST_BUSINESS_ID

TEST_FILE_ID = str(uuid4())

_df = generate_retail_dataset(num_orders=30)

TEST_FILE_RECORD = {
    "id": TEST_FILE_ID,
    "business_id": TEST_BUSINESS_ID,
    "original_filename": "sales.csv",
    "storage_path": f"/tmp/storage/{TEST_FILE_ID}_sales.csv",
    "status": "mapped",
}

TEST_MAPPING_RECORD = {
    "file_id": TEST_FILE_ID,
    "business_id": TEST_BUSINESS_ID,
    "mappings": [
        {"target_field": "order_id", "source_sheet": "Sheet1", "source_column": "order_id"},
        {"target_field": "order_date", "source_sheet": "Sheet1", "source_column": "order_date"},
        {"target_field": "customer_id", "source_sheet": "Sheet1", "source_column": "customer_id"},
        {"target_field": "product_name", "source_sheet": "Sheet1", "source_column": "product_name"},
        {"target_field": "category", "source_sheet": "Sheet1", "source_column": "category"},
        {"target_field": "quantity", "source_sheet": "Sheet1", "source_column": "quantity"},
        {"target_field": "total_revenue", "source_sheet": "Sheet1", "source_column": "total_revenue"},
    ],
    "status": "confirmed",
}


class TestAnalyzeFileAPI:
    """Tests for POST /api/v1/businesses/{business_id}/uploads/{file_id}/analyze."""

    @pytest.mark.asyncio
    async def test_returns_401_without_token(self, client):
        """Unauthenticated analyze request should return 401."""
        response = await client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/analyze"
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_400_if_mapping_not_confirmed(
        self, authenticated_client, mock_supabase
    ):
        """Requesting analysis on an unmapped file should return 400."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        # uploaded_file found
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = [
            type("Res", (), {"data": TEST_FILE_RECORD})(),
            type("Res", (), {"data": None})(),  # No mapping
        ]

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/analyze"
        )
        assert response.status_code == 400
        assert "mapping has not been confirmed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_analyze_success(self, authenticated_client, mock_supabase):
        """Successful analysis run should compute KPIs and return FullAnalyticsReport."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = [
            type("Res", (), {"data": TEST_FILE_RECORD})(),
            type("Res", (), {"data": TEST_MAPPING_RECORD})(),
        ]
        mock_supabase.table.return_value.upsert.return_value.execute.return_value.data = [{}]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{}]

        # Mock reading raw file to return normalized df
        with patch("app.api.v1.analytics.load_canonical_data_from_file", return_value=_df):
            response = await authenticated_client.post(
                f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/analyze"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["file_id"] == TEST_FILE_ID
            assert data["kpis"]["total_revenue"] > 0
            assert len(data["sales"]["monthly_trends"]) > 0
            assert len(data["products"]["top_products"]) > 0
            assert "data_overview" in data["available_capabilities"]


class TestGetAnalyticsAPI:
    """Tests for GET /api/v1/businesses/{business_id}/uploads/{file_id}/analytics."""

    @pytest.mark.asyncio
    async def test_get_analytics_404_if_not_found(
        self, authenticated_client, mock_supabase
    ):
        """Should return 404 if analytics results have not been generated yet."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = None

        response = await authenticated_client.get(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/analytics"
        )
        assert response.status_code == 404
