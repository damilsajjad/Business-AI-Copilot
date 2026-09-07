"""Data mapping schemas for canonical business schema alignment."""

from datetime import datetime

from pydantic import BaseModel, Field


class CanonicalField(BaseModel):
    """Definition of a canonical target business field."""

    name: str
    label: str
    description: str
    required: bool
    expected_type: str  # datetime, numeric, id, text, categorical
    category: str  # essential, product, customer, financial, dimension
    example_column_names: list[str] = []


class ColumnMappingItem(BaseModel):
    """A mapping from a source sheet column to a canonical field."""

    target_field: str
    source_sheet: str = "Sheet1"
    source_column: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning: str = ""


class MappingProposalResponse(BaseModel):
    """AI proposed schema mappings for an uploaded file."""

    file_id: str
    mappings: list[ColumnMappingItem]
    unmapped_columns: list[str] = []
    confidence_score: float = 0.0
    suggested_by: str = "heuristic"  # gemini or heuristic


class MappingConfirmationRequest(BaseModel):
    """Payload to confirm column mappings."""

    mappings: list[ColumnMappingItem]


class MappingValidationResult(BaseModel):
    """Outcome of deterministic mapping validation."""

    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []


class DataMappingResponse(BaseModel):
    """Stored confirmed data mapping record."""

    id: str
    business_id: str
    file_id: str
    mappings: list[ColumnMappingItem]
    status: str
    created_at: datetime
    updated_at: datetime
