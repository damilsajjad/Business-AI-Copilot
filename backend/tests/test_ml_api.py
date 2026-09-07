"""Tests for Machine Learning API endpoints."""

from unittest.mock import patch
from uuid import uuid4

import pytest

from app.data.synthetic_data import generate_retail_dataset
from tests.conftest import TEST_BUSINESS_ID

TEST_FILE_ID = str(uuid4())
_df = generate_retail_dataset(num_orders=50)

TEST_FILE_RECORD = {
    "id": TEST_FILE_ID,
    "business_id": TEST_BUSINESS_ID,
    "original_filename": "retail_sales.csv",
    "storage_path": f"/tmp/storage/{TEST_FILE_ID}_retail_sales.csv",
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


class TestMLForecastingAPI:
    """Tests for POST and GET /ml/forecast endpoints."""

    @pytest.mark.asyncio
    async def test_forecast_endpoint_success(self, authenticated_client, mock_supabase):
        """Should generate sales forecast and return horizons."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = [
            type("Res", (), {"data": TEST_FILE_RECORD})(),
            type("Res", (), {"data": TEST_MAPPING_RECORD})(),
        ]
        mock_supabase.table.return_value.upsert.return_value.execute.return_value.data = [{}]

        with patch("app.api.v1.ml.load_canonical_data_from_file", return_value=_df):
            response = await authenticated_client.post(
                f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/ml/forecast"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["file_id"] == TEST_FILE_ID
            assert len(data["horizon_30_days"]) == 30
            assert data["projected_30d_revenue"] > 0


class TestMLChurnAPI:
    """Tests for POST and GET /ml/churn endpoints."""

    @pytest.mark.asyncio
    async def test_churn_endpoint_success(self, authenticated_client, mock_supabase):
        """Should evaluate churn risk and return customer risk breakdown."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = [
            type("Res", (), {"data": TEST_FILE_RECORD})(),
            type("Res", (), {"data": TEST_MAPPING_RECORD})(),
        ]
        mock_supabase.table.return_value.upsert.return_value.execute.return_value.data = [{}]

        with patch("app.api.v1.ml.load_canonical_data_from_file", return_value=_df):
            response = await authenticated_client.post(
                f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/ml/churn"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["file_id"] == TEST_FILE_ID
            assert data["total_customers_evaluated"] > 0
            assert len(data["customers"]) > 0
