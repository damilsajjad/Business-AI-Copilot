"""Data mapping and AI proposal API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.auth import BusinessUser
from app.core.supabase import SupabaseClientError, get_supabase_client
from app.schemas.mapping import (
    CanonicalField,
    DataMappingResponse,
    MappingConfirmationRequest,
    MappingProposalResponse,
    MappingValidationResult,
)
from app.schemas.profiler import DataProfileResponse
from app.services.canonical_schema import CANONICAL_FIELDS
from app.services.llm_mapper import propose_mapping_with_gemini
from app.services.mapping_validator import validate_mapping

router = APIRouter(tags=["mappings"])


@router.get("/canonical-schema", response_model=list[CanonicalField])
async def get_canonical_schema() -> list[CanonicalField]:
    """Return the standard target business canonical fields and descriptions."""
    return CANONICAL_FIELDS


@router.post(
    "/businesses/{business_id}/uploads/{file_id}/mapping/propose",
    response_model=MappingProposalResponse,
)
async def propose_file_mapping(
    business_user: BusinessUser,
    file_id: UUID,
) -> MappingProposalResponse:
    """Generate AI-suggested column mappings for an uploaded file profile."""
    try:
        client = get_supabase_client()
        result = (
            client.table("uploaded_files")
            .select("metadata")
            .eq("id", str(file_id))
            .eq("business_id", str(business_user["business_id"]))
            .single()
            .execute()
        )

        if not result.data or not result.data.get("metadata"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uploaded file or profile not found",
            )

        profile = DataProfileResponse(**result.data["metadata"])
        return await propose_mapping_with_gemini(profile)

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
            detail=f"Failed to generate mapping proposal: {e}",
        ) from e


@router.post(
    "/businesses/{business_id}/uploads/{file_id}/mapping/validate",
    response_model=MappingValidationResult,
)
async def validate_file_mapping(
    business_user: BusinessUser,
    file_id: UUID,
    body: MappingConfirmationRequest,
) -> MappingValidationResult:
    """Validate proposed column mappings against the dataset profile without saving."""
    try:
        client = get_supabase_client()
        result = (
            client.table("uploaded_files")
            .select("metadata")
            .eq("id", str(file_id))
            .eq("business_id", str(business_user["business_id"]))
            .single()
            .execute()
        )

        if not result.data or not result.data.get("metadata"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uploaded file or profile not found",
            )

        profile = DataProfileResponse(**result.data["metadata"])
        return validate_mapping(body.mappings, profile)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mapping validation failed: {e}",
        ) from e


@router.post(
    "/businesses/{business_id}/uploads/{file_id}/mapping/confirm",
    response_model=DataMappingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def confirm_file_mapping(
    business_user: BusinessUser,
    file_id: UUID,
    body: MappingConfirmationRequest,
) -> DataMappingResponse:
    """Validate and persist confirmed column mappings for downstream analytics."""
    try:
        client = get_supabase_client()
        file_result = (
            client.table("uploaded_files")
            .select("metadata")
            .eq("id", str(file_id))
            .eq("business_id", str(business_user["business_id"]))
            .single()
            .execute()
        )

        if not file_result.data or not file_result.data.get("metadata"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uploaded file not found",
            )

        profile = DataProfileResponse(**file_result.data["metadata"])

        # 1. Deterministic validation check
        validation = validate_mapping(body.mappings, profile)
        if not validation.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid mapping configuration: {'; '.join(validation.errors)}",
            )

        # 2. Persist in data_mappings table
        mapping_record = {
            "business_id": str(business_user["business_id"]),
            "file_id": str(file_id),
            "mappings": [m.model_dump() for m in body.mappings],
            "status": "confirmed",
        }

        mapping_result = (
            client.table("data_mappings")
            .upsert(mapping_record, on_conflict="business_id,file_id")
            .execute()
        )

        if not mapping_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save data mapping record",
            )

        # 3. Update uploaded_files status to 'mapped'
        client.table("uploaded_files").update({"status": "mapped"}).eq("id", str(file_id)).execute()

        return DataMappingResponse(**mapping_result.data[0])

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
            detail=f"Failed to confirm mapping: {e}",
        ) from e


@router.get(
    "/businesses/{business_id}/uploads/{file_id}/mapping",
    response_model=DataMappingResponse,
)
async def get_confirmed_mapping(
    business_user: BusinessUser,
    file_id: UUID,
) -> DataMappingResponse:
    """Retrieve existing confirmed mapping for a file."""
    try:
        client = get_supabase_client()
        result = (
            client.table("data_mappings")
            .select("*")
            .eq("file_id", str(file_id))
            .eq("business_id", str(business_user["business_id"]))
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No confirmed mapping found for this file",
            )

        return DataMappingResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve data mapping: {e}",
        ) from e
