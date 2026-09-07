"""Tests for Scheduled Executive Reports API endpoints."""

from uuid import uuid4

import pytest

from tests.conftest import TEST_BUSINESS_ID

TEST_REPORT_RECORD = {
    "id": str(uuid4()),
    "business_id": TEST_BUSINESS_ID,
    "report_type": "weekly",
    "status": "active",
    "last_generated_at": "2026-09-01T00:00:00Z",
    "last_report_content": {},
    "created_at": "2026-09-01T00:00:00Z",
}


class TestReportsAPI:
    """Integration tests for Scheduled Reports endpoints."""

    @pytest.mark.asyncio
    async def test_list_scheduled_reports(self, authenticated_client, mock_supabase):
        """Should return scheduled report configurations for business."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            TEST_REPORT_RECORD
        ]

        response = await authenticated_client.get(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/reports/schedule"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["report_type"] == "weekly"

    @pytest.mark.asyncio
    async def test_configure_scheduled_report(self, authenticated_client, mock_supabase):
        """Should configure or update a scheduled report setting."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.upsert.return_value.select.return_value.single.return_value.execute.return_value.data = (
            TEST_REPORT_RECORD
        )

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/reports/schedule",
            json={"report_type": "weekly", "status": "active"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_trigger_cron_reports(self, client, mock_supabase):
        """Should trigger background cron processing for active schedules."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            TEST_REPORT_RECORD
        ]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{}]

        response = await client.post("/api/v1/reports/cron/trigger")
        assert response.status_code == 200
        data = response.json()
        assert data["triggered_reports_count"] == 1
        assert data["status"] == "success"
