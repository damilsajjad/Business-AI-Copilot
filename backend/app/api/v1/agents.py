import contextlib
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.agents.copilot import answer_copilot_query
from app.agents.orchestrator import run_multi_agent_synthesis
from app.core.auth import BusinessUser
from app.core.supabase import SupabaseClientError, get_supabase_client
from app.schemas.agents import (
    CopilotChatRequest,
    CopilotChatResponse,
    ExecutiveBriefReport,
)
from app.schemas.analytics import FullAnalyticsReport
from app.schemas.ml import CustomerChurnResponse, SalesForecastResponse

router = APIRouter(prefix="/businesses/{business_id}/uploads/{file_id}", tags=["agents"])


def _fetch_context(client, business_id: str, file_id: str):
    """Fetch pre-computed analytics, forecasts, and churn evaluations for a file."""
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
            detail="Analytics have not been computed yet for this file. Please run analysis first.",
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


@router.post("/insights/generate", response_model=ExecutiveBriefReport)
async def generate_insights_endpoint(
    business_user: BusinessUser,
    file_id: UUID,
) -> ExecutiveBriefReport:
    """Run multi-agent synthesis to generate comprehensive executive brief."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)

    try:
        client = get_supabase_client()
        analytics, forecast, churn = _fetch_context(client, business_id, file_id_str)

        brief = await run_multi_agent_synthesis(analytics, forecast, churn)

        # Upsert into ai_insights table
        client.table("ai_insights").upsert(
            {
                "business_id": business_id,
                "file_id": file_id_str,
                "insights": brief.model_dump(mode="json"),
            },
            on_conflict="business_id,file_id",
        ).execute()

        return brief

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
            detail=f"Insights generation failed: {e}",
        ) from e


@router.get("/insights", response_model=ExecutiveBriefReport)
async def get_insights_endpoint(
    business_user: BusinessUser,
    file_id: UUID,
) -> ExecutiveBriefReport:
    """Retrieve pre-computed multi-agent executive brief."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)

    try:
        client = get_supabase_client()
        res = (
            client.table("ai_insights")
            .select("insights")
            .eq("file_id", file_id_str)
            .eq("business_id", business_id)
            .single()
            .execute()
        )
        if not res.data or not res.data.get("insights"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Insights have not been generated yet for this file.",
            )
        return ExecutiveBriefReport(**res.data["insights"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve insights: {e}",
        ) from e


@router.post("/copilot/chat", response_model=CopilotChatResponse)
async def copilot_chat_endpoint(
    business_user: BusinessUser,
    file_id: UUID,
    payload: CopilotChatRequest,
) -> CopilotChatResponse:
    """Interactive conversational Copilot Q&A grounded strictly in business data."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)
    user_id = str(business_user.get("user_id") or business_user.get("id") or "")

    try:
        client = get_supabase_client()
        analytics, forecast, churn = _fetch_context(client, business_id, file_id_str)

        response = await answer_copilot_query(
            query=payload.message,
            history=payload.history,
            analytics=analytics,
            forecast=forecast,
            churn=churn,
        )

        # Log conversation messages
        with contextlib.suppress(Exception):
            client.table("copilot_messages").insert([
                {
                    "business_id": business_id,
                    "file_id": file_id_str,
                    "user_id": user_id,
                    "role": "user",
                    "content": payload.message,
                },
                {
                    "business_id": business_id,
                    "file_id": file_id_str,
                    "user_id": user_id,
                    "role": "assistant",
                    "content": response.reply,
                    "context": response.cited_metrics,
                },
            ]).execute()

        return response

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
            detail=f"Copilot chat failed: {e}",
        ) from e
