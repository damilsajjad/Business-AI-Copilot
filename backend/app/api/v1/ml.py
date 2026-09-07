"""Machine Learning API endpoints for Sales Forecasting and Customer Churn."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.analytics.data_loader import load_canonical_data_from_file
from app.core.auth import BusinessUser
from app.core.supabase import SupabaseClientError, get_supabase_client
from app.ml.churn import calculate_customer_churn_risk
from app.ml.forecasting import generate_sales_forecast
from app.schemas.ml import CustomerChurnResponse, SalesForecastResponse

router = APIRouter(prefix="/businesses/{business_id}/uploads/{file_id}/ml", tags=["machine-learning"])


def _load_canonical_data(client, business_id: str, file_id: str):
    """Helper to fetch metadata, mappings, and load normalized canonical dataframe."""
    file_res = (
        client.table("uploaded_files")
        .select("*")
        .eq("id", file_id)
        .eq("business_id", business_id)
        .single()
        .execute()
    )
    if not file_res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uploaded file not found")

    file_record = file_res.data

    mapping_res = (
        client.table("data_mappings")
        .select("*")
        .eq("file_id", file_id)
        .eq("business_id", business_id)
        .single()
        .execute()
    )
    if not mapping_res.data or not mapping_res.data.get("mappings"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File mapping not confirmed yet. Please confirm column mapping first.",
        )

    mappings = mapping_res.data["mappings"]
    df = load_canonical_data_from_file(
        storage_path=file_record["storage_path"],
        original_filename=file_record["original_filename"],
        mappings=mappings,
    )
    return df


@router.post("/forecast", response_model=SalesForecastResponse)
async def generate_forecast_endpoint(
    business_user: BusinessUser,
    file_id: UUID,
) -> SalesForecastResponse:
    """Generate and persist 30/60/90 day sales forecast projections."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)

    try:
        client = get_supabase_client()
        df = _load_canonical_data(client, business_id, file_id_str)

        result = generate_sales_forecast(df, file_id_str, business_id)

        # Store in ml_forecasts table
        client.table("ml_forecasts").upsert(
            {
                "business_id": business_id,
                "file_id": file_id_str,
                "forecast_type": "sales",
                "results": result.model_dump(mode="json"),
            },
            on_conflict="business_id,file_id,forecast_type",
        ).execute()

        return result

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
            detail=f"Forecasting generation failed: {e}",
        ) from e


@router.get("/forecast", response_model=SalesForecastResponse)
async def get_forecast_endpoint(
    business_user: BusinessUser,
    file_id: UUID,
) -> SalesForecastResponse:
    """Retrieve pre-computed sales forecast."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)

    try:
        client = get_supabase_client()
        res = (
            client.table("ml_forecasts")
            .select("results")
            .eq("file_id", file_id_str)
            .eq("business_id", business_id)
            .eq("forecast_type", "sales")
            .single()
            .execute()
        )
        if not res.data or not res.data.get("results"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forecast not generated yet for this file",
            )
        return SalesForecastResponse(**res.data["results"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve forecast: {e}",
        ) from e


@router.post("/churn", response_model=CustomerChurnResponse)
async def generate_churn_endpoint(
    business_user: BusinessUser,
    file_id: UUID,
) -> CustomerChurnResponse:
    """Evaluate and persist customer churn risk scores."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)

    try:
        client = get_supabase_client()
        df = _load_canonical_data(client, business_id, file_id_str)

        result = calculate_customer_churn_risk(df, file_id_str, business_id)

        # Store in ml_forecasts table
        client.table("ml_forecasts").upsert(
            {
                "business_id": business_id,
                "file_id": file_id_str,
                "forecast_type": "churn",
                "results": result.model_dump(mode="json"),
            },
            on_conflict="business_id,file_id,forecast_type",
        ).execute()

        return result

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
            detail=f"Customer churn evaluation failed: {e}",
        ) from e


@router.get("/churn", response_model=CustomerChurnResponse)
async def get_churn_endpoint(
    business_user: BusinessUser,
    file_id: UUID,
) -> CustomerChurnResponse:
    """Retrieve pre-computed customer churn report."""
    business_id = str(business_user["business_id"])
    file_id_str = str(file_id)

    try:
        client = get_supabase_client()
        res = (
            client.table("ml_forecasts")
            .select("results")
            .eq("file_id", file_id_str)
            .eq("business_id", business_id)
            .eq("forecast_type", "churn")
            .single()
            .execute()
        )
        if not res.data or not res.data.get("results"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer churn risk not evaluated yet for this file",
            )
        return CustomerChurnResponse(**res.data["results"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve churn evaluation: {e}",
        ) from e
