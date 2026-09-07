"""Deterministic analytics execution and retrieval API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.analytics.data_loader import load_canonical_data_from_file
from app.analytics.engine import run_deterministic_analytics
from app.core.auth import BusinessUser
from app.core.supabase import SupabaseClientError, get_supabase_client
from app.schemas.analytics import FullAnalyticsReport

router = APIRouter(prefix="/businesses/{business_id}/uploads/{file_id}", tags=["analytics"])


@router.post("/analyze", response_model=FullAnalyticsReport, status_code=status.HTTP_200_OK)
async def analyze_file_data(
    business_user: BusinessUser,
    file_id: UUID,
) -> FullAnalyticsReport:
    """Run full deterministic analytics on a mapped dataset and persist computed results."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)

    try:
        client = get_supabase_client()

        # 1. Fetch uploaded file metadata
        file_res = (
            client.table("uploaded_files")
            .select("*")
            .eq("id", file_id_str)
            .eq("business_id", business_id)
            .single()
            .execute()
        )

        if not file_res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uploaded file not found",
            )

        file_record = file_res.data

        # 2. Fetch confirmed data mapping
        mapping_res = (
            client.table("data_mappings")
            .select("*")
            .eq("file_id", file_id_str)
            .eq("business_id", business_id)
            .single()
            .execute()
        )

        if not mapping_res.data or not mapping_res.data.get("mappings"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File column mapping has not been confirmed yet. Please confirm mappings first.",
            )

        mappings = mapping_res.data["mappings"]

        # 3. Load normalized canonical DataFrame
        df = load_canonical_data_from_file(
            storage_path=file_record["storage_path"],
            original_filename=file_record["original_filename"],
            mappings=mappings,
        )

        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid records found in dataset after applying column mappings.",
            )

        # 4. Run deterministic analytics
        report = run_deterministic_analytics(
            df=df,
            file_id=file_id_str,
            business_id=business_id,
        )

        # 5. Persist analytics results in database
        analytics_record = {
            "business_id": business_id,
            "file_id": file_id_str,
            "results": report.model_dump(mode="json"),
        }

        client.table("analytics_results").upsert(
            analytics_record,
            on_conflict="business_id,file_id",
        ).execute()

        # 6. Update uploaded_files status to ready
        client.table("uploaded_files").update({"status": "ready"}).eq("id", file_id_str).execute()

        return report

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
            detail=f"Deterministic analytics execution failed: {e}",
        ) from e


@router.get("/analytics", response_model=FullAnalyticsReport)
async def get_analytics_results(
    business_user: BusinessUser,
    file_id: UUID,
) -> FullAnalyticsReport:
    """Retrieve pre-computed deterministic analytics results for a file."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)

    try:
        client = get_supabase_client()

        res = (
            client.table("analytics_results")
            .select("results")
            .eq("file_id", file_id_str)
            .eq("business_id", business_id)
            .single()
            .execute()
        )

        if not res.data or not res.data.get("results"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analytics results not found for this file. Please run analysis first.",
            )

        return FullAnalyticsReport(**res.data["results"])

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
            detail=f"Failed to retrieve analytics results: {e}",
        ) from e
