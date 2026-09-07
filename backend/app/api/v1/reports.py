"""Scheduled Executive Reports API endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.core.auth import BusinessUser
from app.core.supabase import SupabaseClientError, get_supabase_client
from app.schemas.reports import (
    ScheduledReportConfig,
    ScheduleReportRequest,
    TriggerCronResponse,
)

router = APIRouter(tags=["reports"])


@router.get("/businesses/{business_id}/reports/schedule", response_model=list[ScheduledReportConfig])
async def list_scheduled_reports(
    business_user: BusinessUser,
) -> list[ScheduledReportConfig]:
    """Retrieve scheduled report settings for a business workspace."""
    business_id = str(business_user["business_id"])

    try:
        client = get_supabase_client()
        res = (
            client.table("scheduled_reports")
            .select("*")
            .eq("business_id", business_id)
            .execute()
        )
        return [ScheduledReportConfig(**item) for item in (res.data or [])]
    except HTTPException:
        raise
    except SupabaseClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service not configured",
        ) from exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scheduled reports: {e}",
        ) from e


@router.post("/businesses/{business_id}/reports/schedule", response_model=ScheduledReportConfig)
async def configure_scheduled_report(
    business_user: BusinessUser,
    payload: ScheduleReportRequest,
) -> ScheduledReportConfig:
    """Create or update scheduled weekly/monthly executive brief trigger."""
    business_id = str(business_user["business_id"])

    if payload.report_type not in ["weekly", "monthly"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report type")

    try:
        client = get_supabase_client()
        upsert_payload = {
            "business_id": business_id,
            "report_type": payload.report_type,
            "status": payload.status,
            "last_generated_at": datetime.now(UTC).isoformat(),
        }

        res = (
            client.table("scheduled_reports")
            .upsert(upsert_payload, on_conflict="business_id,report_type")
            .select("*")
            .single()
            .execute()
        )

        return ScheduledReportConfig(**res.data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure scheduled report: {e}",
        ) from e


@router.post("/reports/cron/trigger", response_model=TriggerCronResponse)
async def trigger_cron_reports() -> TriggerCronResponse:
    """Background cron trigger endpoint to process periodic scheduled reports."""
    try:
        client = get_supabase_client()
        active_schedules = (
            client.table("scheduled_reports")
            .select("*")
            .eq("status", "active")
            .execute()
        )

        count = len(active_schedules.data or [])
        now_str = datetime.now(UTC).isoformat()

        if count > 0:
            for item in active_schedules.data:
                client.table("scheduled_reports").update(
                    {"last_generated_at": now_str}
                ).eq("id", item["id"]).execute()

        return TriggerCronResponse(
            triggered_reports_count=count,
            message=f"Processed scheduled reports for {count} active subscription(s).",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cron trigger failed: {e}",
        ) from e
