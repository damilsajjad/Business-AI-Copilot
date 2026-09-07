"""Pydantic schemas for Scheduled Executive Reports."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ScheduledReportConfig(BaseModel):
    """Configuration for periodic scheduled executive reports."""

    id: str
    business_id: str
    report_type: str  # "weekly", "monthly"
    status: str  # "active", "paused"
    last_generated_at: datetime | None = None
    last_report_content: dict[str, Any] = {}
    created_at: datetime


class ScheduleReportRequest(BaseModel):
    """Request payload to configure or update scheduled report triggers."""

    report_type: str = "weekly"
    status: str = "active"


class TriggerCronResponse(BaseModel):
    """Response payload for automated background cron trigger executions."""

    triggered_reports_count: int
    status: str = "success"
    message: str
