"""Data profiler Pydantic schemas."""

from typing import Any

from pydantic import BaseModel


class ColumnStats(BaseModel):
    """Statistical summary for numeric or date columns."""

    min: float | str | None = None
    max: float | str | None = None
    mean: float | None = None
    median: float | None = None
    std: float | None = None


class ColumnProfile(BaseModel):
    """Detailed profile of a single dataset column."""

    name: str
    index: int
    detected_type: str  # numeric, datetime, categorical, text, boolean, id
    null_count: int
    null_percentage: float
    unique_count: int
    sample_values: list[Any] = []
    stats: ColumnStats | None = None
    is_likely_id: bool = False
    is_likely_metric: bool = False
    is_likely_dimension: bool = False
    is_likely_date: bool = False
    warnings: list[str] = []


class SheetProfile(BaseModel):
    """Profile of a single sheet / table."""

    sheet_name: str
    row_count: int
    column_count: int
    duplicate_rows_count: int
    columns: list[ColumnProfile]
    warnings: list[str] = []


class DataProfileResponse(BaseModel):
    """Full data profiling result for an uploaded file."""

    file_id: str
    file_name: str
    total_sheets: int
    sheets: list[SheetProfile]
    data_quality_score: float  # 0 to 100
    overall_warnings: list[str] = []
