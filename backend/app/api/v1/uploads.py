"""File upload and data profiling API endpoints."""

from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.auth import BusinessUser
from app.core.config import settings
from app.core.supabase import SupabaseClientError, get_supabase_client
from app.schemas.profiler import DataProfileResponse
from app.schemas.upload import UploadedFileResponse
from app.services.parser import ParsingError, parse_file
from app.services.profiler import profile_dataset
from app.services.storage import storage_service

router = APIRouter(prefix="/businesses/{business_id}/uploads", tags=["uploads"])


@router.post("", response_model=UploadedFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_profile_file(
    business_user: BusinessUser,
    file: Annotated[UploadFile, File(...)],
) -> UploadedFileResponse:
    """Upload a CSV or XLSX file, validate size/format, save to storage, and run profiling."""
    filename = file.filename or "unknown"
    lower_name = filename.lower()

    if not (lower_name.endswith(".csv") or lower_name.endswith(".xlsx") or lower_name.endswith(".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only CSV and Excel (.xlsx) files are supported.",
        )

    file_type = "csv" if lower_name.endswith(".csv") else "xlsx"

    # Read content and check size
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {e}",
        ) from e

    file_size = len(content)
    max_bytes = settings.upload_max_size_mb * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed limit of {settings.upload_max_size_mb}MB.",
        )

    file_id = str(uuid4())
    business_id = str(business_user["business_id"])

    # 1. Parse content
    try:
        sheets_data = parse_file(filename, content)
    except ParsingError as pe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File parsing failed: {pe}",
        ) from pe

    sheet_count = len(sheets_data)

    # 2. Run deterministic profiling
    profile_result = profile_dataset(
        file_id=file_id,
        file_name=filename,
        sheets_dict=sheets_data,
    )

    # 3. Store raw file
    storage_path = storage_service.save_file(
        business_id=business_id,
        file_id=file_id,
        filename=filename,
        content=content,
    )

    # 4. Save metadata to Supabase DB
    record = {
        "id": file_id,
        "business_id": business_id,
        "uploaded_by": business_user["id"],
        "original_filename": filename,
        "storage_path": storage_path,
        "file_type": file_type,
        "file_size_bytes": file_size,
        "status": "profiled",
        "sheet_count": sheet_count,
        "error_message": "",
        "metadata": profile_result.model_dump(),
    }

    try:
        client = get_supabase_client()
        result = client.table("uploaded_files").insert(record).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record uploaded file in database",
            )
        db_record = result.data[0]
        return UploadedFileResponse(**db_record)
    except SupabaseClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service not configured",
        ) from exc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist file record: {e}",
        ) from e


@router.get("", response_model=list[UploadedFileResponse])
async def list_uploaded_files(
    business_user: BusinessUser,
) -> list[UploadedFileResponse]:
    """List all uploaded files for the business."""
    try:
        client = get_supabase_client()
        result = (
            client.table("uploaded_files")
            .select("*")
            .eq("business_id", str(business_user["business_id"]))
            .order("created_at", desc=True)
            .execute()
        )
        return [UploadedFileResponse(**item) for item in result.data or []]
    except SupabaseClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service not configured",
        ) from exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list uploaded files: {e}",
        ) from e


@router.get("/{file_id}", response_model=UploadedFileResponse)
async def get_uploaded_file(
    business_user: BusinessUser,
    file_id: UUID,
) -> UploadedFileResponse:
    """Get metadata for a single uploaded file."""
    try:
        client = get_supabase_client()
        result = (
            client.table("uploaded_files")
            .select("*")
            .eq("id", str(file_id))
            .eq("business_id", str(business_user["business_id"]))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )
        return UploadedFileResponse(**result.data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve file record: {e}",
        ) from e


@router.get("/{file_id}/profile", response_model=DataProfileResponse)
async def get_file_data_profile(
    business_user: BusinessUser,
    file_id: UUID,
) -> DataProfileResponse:
    """Retrieve the deterministic data profiling report for an uploaded file."""
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
                detail="Data profile not found for this file",
            )
        return DataProfileResponse(**result.data["metadata"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve profile: {e}",
        ) from e


@router.post("/sample", response_model=UploadedFileResponse, status_code=status.HTTP_201_CREATED)
async def load_sample_dataset(
    business_user: BusinessUser,
) -> UploadedFileResponse:
    """Instantly generate, profile, and attach realistic sample retail sales data."""
    from app.data.synthetic_data import generate_retail_dataset

    df = generate_retail_dataset(num_orders=350)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    filename = "sample_retail_store_sales.csv"

    file_id = str(uuid4())
    business_id = str(business_user["business_id"])

    sheets_data = {"Sheet1": df}
    profile_result = profile_dataset(
        file_id=file_id,
        file_name=filename,
        sheets_dict=sheets_data,
    )

    storage_path = storage_service.save_file(
        business_id=business_id,
        file_id=file_id,
        filename=filename,
        content=csv_bytes,
    )

    record = {
        "id": file_id,
        "business_id": business_id,
        "uploaded_by": business_user["id"],
        "original_filename": filename,
        "storage_path": storage_path,
        "file_type": "csv",
        "file_size_bytes": len(csv_bytes),
        "status": "profiled",
        "sheet_count": 1,
        "error_message": "",
        "metadata": profile_result.model_dump(),
    }

    try:
        client = get_supabase_client()
        result = client.table("uploaded_files").insert(record).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save sample file record",
            )
        return UploadedFileResponse(**result.data[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate sample dataset: {e}",
        ) from e
