"""Action Items, Scenario Simulation, and Report Export API endpoints."""

import contextlib
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel

from app.actions.exporter import generate_executive_markdown_report
from app.actions.recommendations import generate_action_recommendations
from app.actions.simulator import run_scenario_simulation
from app.agents.orchestrator import run_multi_agent_synthesis
from app.core.auth import BusinessUser
from app.core.supabase import get_supabase_client
from app.schemas.actions import (
    ActionItem,
    WhatIfSimulationRequest,
    WhatIfSimulationResponse,
)
from app.schemas.analytics import FullAnalyticsReport
from app.schemas.ml import CustomerChurnResponse, SalesForecastResponse

router = APIRouter(prefix="/businesses/{business_id}/uploads/{file_id}", tags=["actions"])


class UpdateActionStatusRequest(BaseModel):
    status: str  # "pending", "in_progress", "completed", "dismissed"


def _fetch_all_context(client, business_id: str, file_id: str):
    """Fetch business, analytics, forecast, and churn context."""
    analytics_res = (
        client.table("analytics_results")
        .select("results")
        .eq("file_id", file_id)
        .eq("business_id", business_id)
        .single()
        .execute()
    )
    if not analytics_res.data or not analytics_res.data.get("results"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analytics must be computed first before accessing actions.",
        )

    analytics = FullAnalyticsReport(**analytics_res.data["results"])

    forecast: SalesForecastResponse | None = None
    forecast_res = (
        client.table("ml_forecasts")
        .select("results")
        .eq("file_id", file_id)
        .eq("business_id", business_id)
        .eq("forecast_type", "sales")
        .single()
        .execute()
    )
    if forecast_res.data and forecast_res.data.get("results"):
        with contextlib.suppress(Exception):
            forecast = SalesForecastResponse(**forecast_res.data["results"])

    churn: CustomerChurnResponse | None = None
    churn_res = (
        client.table("ml_forecasts")
        .select("results")
        .eq("file_id", file_id)
        .eq("business_id", business_id)
        .eq("forecast_type", "churn")
        .single()
        .execute()
    )
    if churn_res.data and churn_res.data.get("results"):
        with contextlib.suppress(Exception):
            churn = CustomerChurnResponse(**churn_res.data["results"])

    return analytics, forecast, churn


@router.get("/actions", response_model=list[ActionItem])
async def get_action_items_endpoint(
    business_user: BusinessUser,
    file_id: UUID,
) -> list[ActionItem]:
    """Retrieve action items for this file, generating them if not already saved."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)

    try:
        client = get_supabase_client()
        res = (
            client.table("action_items")
            .select("*")
            .eq("file_id", file_id_str)
            .eq("business_id", business_id)
            .execute()
        )

        if res.data and len(res.data) > 0:
            return [ActionItem(**item) for item in res.data]

        # If none exist, generate and persist default recommendations
        analytics, forecast, churn = _fetch_all_context(client, business_id, file_id_str)
        generated = generate_action_recommendations(analytics, forecast, churn)

        insert_payload = [
            {
                "id": item.id,
                "business_id": business_id,
                "file_id": file_id_str,
                "title": item.title,
                "domain": item.domain,
                "urgency": item.urgency,
                "expected_impact": item.expected_impact,
                "effort": item.effort,
                "timeframe": item.timeframe,
                "action_steps": item.action_steps,
                "owner": item.owner,
                "risk_if_ignored": item.risk_if_ignored,
                "status": item.status,
            }
            for item in generated
        ]

        client.table("action_items").insert(insert_payload).execute()
        return generated

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch actions: {e}",
        ) from e


@router.patch("/actions/{action_id}", response_model=ActionItem)
async def update_action_status_endpoint(
    business_user: BusinessUser,
    file_id: UUID,
    action_id: UUID,
    payload: UpdateActionStatusRequest,
) -> ActionItem:
    """Update progress status of an action item."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)
    action_id_str = str(action_id)

    if payload.status not in ["pending", "in_progress", "completed", "dismissed"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status value")

    try:
        client = get_supabase_client()
        res = (
            client.table("action_items")
            .update({"status": payload.status})
            .eq("id", action_id_str)
            .eq("file_id", file_id_str)
            .eq("business_id", business_id)
            .select("*")
            .single()
            .execute()
        )

        if not res.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action item not found")

        return ActionItem(**res.data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update action status: {e}",
        ) from e


@router.post("/simulate", response_model=WhatIfSimulationResponse)
async def simulate_scenario_endpoint(
    business_user: BusinessUser,
    file_id: UUID,
    payload: WhatIfSimulationRequest,
) -> WhatIfSimulationResponse:
    """Run What-If commercial scenario simulation."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)

    try:
        client = get_supabase_client()
        analytics, _, churn = _fetch_all_context(client, business_id, file_id_str)

        return run_scenario_simulation(analytics, payload, churn)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {e}",
        ) from e


@router.get("/export")
async def export_report_endpoint(
    business_user: BusinessUser,
    file_id: UUID,
):
    """Export complete Executive Intelligence Brief in Markdown format."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)

    try:
        client = get_supabase_client()
        analytics, forecast, churn = _fetch_all_context(client, business_id, file_id_str)

        # Get business name
        biz_res = client.table("businesses").select("name").eq("id", business_id).single().execute()
        biz_name = biz_res.data.get("name", "Business Workspace") if biz_res.data else "Business Workspace"

        # Get actions
        actions = generate_action_recommendations(analytics, forecast, churn)
        brief = await run_multi_agent_synthesis(analytics, forecast, churn)

        md_content = generate_executive_markdown_report(
            business_name=biz_name,
            analytics=analytics,
            brief=brief,
            actions=actions,
            forecast=forecast,
            churn=churn,
        )

        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="Executive_Brief_{file_id_str[:8]}.md"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report export failed: {e}",
        ) from e
