"""Upload-related Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class UploadedFileResponse(BaseModel):
    """Metadata response for an uploaded file."""

    id: str
    business_id: str
    uploaded_by: str | None = None
    original_filename: str
    storage_path: str
    file_type: str
    file_size_bytes: int
    status: str
    sheet_count: int = 1
    error_message: str = ""
    created_at: datetime
    updated_at: datetime
