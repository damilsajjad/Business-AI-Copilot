"""Tests for Actions and What-If simulation API endpoints."""

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


class TestActionsAPI:
    """Tests for GET /actions, POST /simulate, and GET /export."""

    @pytest.mark.asyncio
    async def test_get_action_items_generates_and_returns(
        self, authenticated_client, mock_supabase
    ):
        """Should generate and return action items when none exist in database."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        # First check returns empty list for existing actions
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.side_effect = [
            type("Res", (), {"data": [{"role": "owner"}]})(),
            type("Res", (), {"data": []})(),
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = [
            type("Res", (), {"data": TEST_ANALYTICS_RECORD})(),
            type("Res", (), {"data": None})(),
            type("Res", (), {"data": None})(),
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{}]

        response = await authenticated_client.get(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/actions"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    @pytest.mark.asyncio
    async def test_simulate_scenario_success(
        self, authenticated_client, mock_supabase
    ):
        """Should run simulation and return projected revenue."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = [
            type("Res", (), {"data": TEST_ANALYTICS_RECORD})(),
            type("Res", (), {"data": None})(),
            type("Res", (), {"data": None})(),
        ]

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/simulate",
            json={"revenue_growth_pct": 15.0, "price_change_pct": 0.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["simulated_revenue"] > data["current_revenue"]
        assert data["revenue_delta"] > 0
