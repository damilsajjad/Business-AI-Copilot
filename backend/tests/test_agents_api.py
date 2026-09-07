"""Tests for Multi-Agent & Copilot API endpoints."""

from uuid import uuid4

import pytest

from app.analytics.engine import run_deterministic_analytics
from app.data.synthetic_data import generate_retail_dataset
from tests.conftest import TEST_BUSINESS_ID

TEST_FILE_ID = str(uuid4())
_df = generate_retail_dataset(num_orders=50)
_analytics = run_deterministic_analytics(_df, TEST_FILE_ID, TEST_BUSINESS_ID)

TEST_ANALYTICS_RECORD = {
    "file_id": TEST_FILE_ID,
    "business_id": TEST_BUSINESS_ID,
    "results": _analytics.model_dump(mode="json"),
}


class TestAgentsAPI:
    """Tests for POST /insights/generate and POST /copilot/chat."""

    @pytest.mark.asyncio
    async def test_generate_insights_success(self, authenticated_client, mock_supabase):
        """Should synthesize executive brief and return 200."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = [
            type("Res", (), {"data": TEST_ANALYTICS_RECORD})(),
            type("Res", (), {"data": None})(),  # No saved forecast
            type("Res", (), {"data": None})(),  # No saved churn
        ]
        mock_supabase.table.return_value.upsert.return_value.execute.return_value.data = [{}]

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/insights/generate"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["file_id"] == TEST_FILE_ID
        assert data["health_score"] >= 0
        assert len(data["domain_insights"]) > 0

    @pytest.mark.asyncio
    async def test_copilot_chat_endpoint_success(self, authenticated_client, mock_supabase):
        """Should answer user query grounded in dataset metrics."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = [
            type("Res", (), {"data": TEST_ANALYTICS_RECORD})(),
            type("Res", (), {"data": None})(),
            type("Res", (), {"data": None})(),
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{}]

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/copilot/chat",
            json={"message": "What is our total revenue?", "history": []},
        )
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert f"${_analytics.kpis.total_revenue:,.2f}" in data["reply"]
