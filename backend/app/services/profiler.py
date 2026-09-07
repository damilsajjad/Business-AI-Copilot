"""Deterministic data profiling service."""

import math
from typing import Any

import numpy as np
import pandas as pd

from app.schemas.profiler import (
    ColumnProfile,
    ColumnStats,
    DataProfileResponse,
    SheetProfile,
)


def _safe_float(val: Any) -> float | None:
    """Convert value to float if valid and not NaN/Inf."""
    if val is None or pd.isna(val):
        return None
    try:
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else round(f, 4)
    except (ValueError, TypeError):
        return None


def _detect_datetime_series(series: pd.Series) -> tuple[bool, pd.Series | None]:
    """Check if a series can reliably be parsed as datetime."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return True, series

    # If it's an object/string series, sample non-null values
    non_null = series.dropna()
    if len(non_null) == 0:
        return False, None

    sample = non_null.head(50).astype(str)
    try:
        converted = pd.to_datetime(sample, errors="coerce")
        success_ratio = converted.notna().sum() / len(sample)
        if success_ratio >= 0.8:
            full_converted = pd.to_datetime(series, errors="coerce")
            return True, full_converted
    except Exception:
        pass

    return False, None


def _infer_column_roles(
    name: str,
    detected_type: str,
    unique_count: int,
    row_count: int,
) -> tuple[bool, bool, bool, bool]:
    """Infer semantic flags: (is_id, is_metric, is_dimension, is_date)."""
    clean_name = name.lower().strip()
    is_id = False
    is_metric = False
    is_dimension = False
    is_date = detected_type == "datetime"

    id_keywords = ["id", "uuid", "sku", "code", "key", "number", "num", "#"]
    metric_keywords = [
        "amount", "price", "revenue", "sales", "cost", "total", "qty",
        "quantity", "units", "discount", "profit", "margin", "tax", "fee",
        "rate", "score", "value", "balance"
    ]

    # Identifier inference
    if any(clean_name == kw or clean_name.endswith(f"_{kw}") or clean_name.startswith(f"{kw}_") for kw in id_keywords) or row_count > 10 and unique_count == row_count and detected_type in ("numeric", "text"):
        is_id = True

    # Metric inference
    if detected_type == "numeric" and not is_id and (any(kw in clean_name for kw in metric_keywords) or unique_count > 5):
        is_metric = True

    # Dimension inference
    if detected_type in ("categorical", "boolean", "text") and not is_id or detected_type == "numeric" and not is_id and unique_count <= 5 and not is_metric:
        is_dimension = True

    return is_id, is_metric, is_dimension, is_date


def profile_column(series: pd.Series, col_index: int, row_count: int) -> ColumnProfile:
    """Compute detailed profile for a single column."""
    col_name = str(series.name)
    null_count = int(series.isna().sum())
    null_percentage = round((null_count / row_count * 100), 2) if row_count > 0 else 0.0
    non_null_series = series.dropna()
    unique_count = int(non_null_series.nunique())
    warnings: list[str] = []

    # Get sample values (clean JSON serializable)
    sample_values = []
    for val in non_null_series.head(5):
        if pd.isna(val):
            continue
        if isinstance(val, (np.integer, int)):
            sample_values.append(int(val))
        elif isinstance(val, (np.floating, float)):
            sample_values.append(round(float(val), 4))
        elif isinstance(val, (pd.Timestamp, np.datetime64)):
            sample_values.append(str(val))
        else:
            sample_values.append(str(val))

    # Type detection and stats calculation
    is_dt, dt_series = _detect_datetime_series(series)
    stats: ColumnStats | None = None
    detected_type = "unknown"

    if is_dt and dt_series is not None:
        detected_type = "datetime"
        valid_dts = dt_series.dropna()
        if not valid_dts.empty:
            stats = ColumnStats(
                min=str(valid_dts.min()),
                max=str(valid_dts.max()),
            )
    elif pd.api.types.is_bool_dtype(series) or (unique_count == 2 and set(non_null_series.astype(str).str.lower()).issubset({"true", "false", "0", "1", "yes", "no"})):
        detected_type = "boolean"
    elif pd.api.types.is_numeric_dtype(series):
        detected_type = "numeric"
        if not non_null_series.empty:
            stats = ColumnStats(
                min=_safe_float(non_null_series.min()),
                max=_safe_float(non_null_series.max()),
                mean=_safe_float(non_null_series.mean()),
                median=_safe_float(non_null_series.median()),
                std=_safe_float(non_null_series.std()),
            )
    else:
        # Check if numeric coercible
        numeric_attempt = pd.to_numeric(non_null_series, errors="coerce")
        if len(non_null_series) > 0 and (numeric_attempt.notna().sum() / len(non_null_series)) >= 0.85:
            detected_type = "numeric"
            valid_nums = numeric_attempt.dropna()
            stats = ColumnStats(
                min=_safe_float(valid_nums.min()),
                max=_safe_float(valid_nums.max()),
                mean=_safe_float(valid_nums.mean()),
                median=_safe_float(valid_nums.median()),
                std=_safe_float(valid_nums.std()),
            )
        elif unique_count <= 30 or (row_count > 0 and (unique_count / row_count) < 0.2):
            detected_type = "categorical"
        else:
            detected_type = "text"

    # Warnings
    if null_percentage == 100.0:
        warnings.append("Column is 100% empty (all values are null).")
    elif null_percentage > 40.0:
        warnings.append(f"High null rate: {null_percentage}% missing values.")

    if unique_count == 1 and row_count > 1:
        warnings.append("Constant column: contains only a single distinct value.")

    is_id, is_metric, is_dimension, is_date = _infer_column_roles(
        col_name, detected_type, unique_count, row_count
    )

    return ColumnProfile(
        name=col_name,
        index=col_index,
        detected_type=detected_type,
        null_count=null_count,
        null_percentage=null_percentage,
        unique_count=unique_count,
        sample_values=sample_values,
        stats=stats,
        is_likely_id=is_id,
        is_likely_metric=is_metric,
        is_likely_dimension=is_dimension,
        is_likely_date=is_date,
        warnings=warnings,
    )


def profile_sheet(sheet_name: str, df: pd.DataFrame) -> SheetProfile:
    """Profile a single sheet / dataframe."""
    row_count = len(df)
    col_count = len(df.columns)
    warnings: list[str] = []

    if row_count == 0:
        warnings.append("Sheet has 0 rows of data.")
        return SheetProfile(
            sheet_name=sheet_name,
            row_count=0,
            column_count=col_count,
            duplicate_rows_count=0,
            columns=[],
            warnings=warnings,
        )

    # Check for duplicate rows
    duplicate_rows_count = int(df.duplicated().sum())
    if duplicate_rows_count > 0:
        dup_pct = round((duplicate_rows_count / row_count * 100), 1)
        if dup_pct > 10:
            warnings.append(f"Contains {duplicate_rows_count} duplicate rows ({dup_pct}%).")

    columns = [
        profile_column(df[col], idx, row_count)
        for idx, col in enumerate(df.columns)
    ]

    return SheetProfile(
        sheet_name=sheet_name,
        row_count=row_count,
        column_count=col_count,
        duplicate_rows_count=duplicate_rows_count,
        columns=columns,
        warnings=warnings,
    )


def profile_dataset(
    file_id: str,
    file_name: str,
    sheets_dict: dict[str, pd.DataFrame],
) -> DataProfileResponse:
    """Run full deterministic profiling across all sheets in a dataset."""
    sheet_profiles = []
    overall_warnings: list[str] = []
    total_null_pcts = []

    for name, df in sheets_dict.items():
        sp = profile_sheet(name, df)
        sheet_profiles.append(sp)
        for col in sp.columns:
            total_null_pcts.append(col.null_percentage)

    # Quality score calculation (0 to 100)
    score = 100.0
    if not sheet_profiles or all(s.row_count == 0 for s in sheet_profiles):
        score = 0.0
        overall_warnings.append("Dataset contains no records.")
    else:
        # Penalize average null percentage
        avg_null = sum(total_null_pcts) / len(total_null_pcts) if total_null_pcts else 0.0
        score -= min(40.0, avg_null * 0.8)

        # Penalize duplicate rows
        total_rows = sum(s.row_count for s in sheet_profiles)
        total_dups = sum(s.duplicate_rows_count for s in sheet_profiles)
        if total_rows > 0:
            dup_ratio = total_dups / total_rows
            score -= min(20.0, dup_ratio * 50)

    score = max(0.0, min(100.0, round(score, 1)))

    return DataProfileResponse(
        file_id=file_id,
        file_name=file_name,
        total_sheets=len(sheet_profiles),
        sheets=sheet_profiles,
        data_quality_score=score,
        overall_warnings=overall_warnings,
    )
