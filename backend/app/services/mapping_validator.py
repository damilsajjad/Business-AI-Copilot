"""Deterministic validation engine for column mappings against dataset profiles."""

from app.schemas.mapping import (
    ColumnMappingItem,
    MappingValidationResult,
)
from app.schemas.profiler import ColumnProfile, DataProfileResponse
from app.services.canonical_schema import CANONICAL_FIELD_MAP


def validate_mapping(
    mappings: list[ColumnMappingItem],
    profile: DataProfileResponse,
) -> MappingValidationResult:
    """Perform strict deterministic validation on column mappings against dataset profile."""
    errors: list[str] = []
    warnings: list[str] = []

    # Index dataset profile by sheet and column name
    sheet_column_map: dict[str, dict[str, ColumnProfile]] = {}
    for sheet in profile.sheets:
        sheet_column_map[sheet.sheet_name] = {col.name: col for col in sheet.columns}

    # If only 1 sheet exists, allow default fallback sheet name
    default_sheet_name = profile.sheets[0].sheet_name if profile.sheets else "Sheet1"

    mapped_targets: set[str] = set()
    mapped_sources: set[tuple[str, str]] = set()

    for item in mappings:
        target = item.target_field
        sheet_name = item.source_sheet if item.source_sheet in sheet_column_map else default_sheet_name
        col_name = item.source_column

        # 1. Target field validity
        if target not in CANONICAL_FIELD_MAP:
            errors.append(f"Unknown target canonical field: '{target}'.")
            continue

        canonical_def = CANONICAL_FIELD_MAP[target]

        # 2. Source column existence
        if sheet_name not in sheet_column_map:
            errors.append(f"Source sheet '{sheet_name}' does not exist in dataset.")
            continue

        cols_in_sheet = sheet_column_map[sheet_name]
        if col_name not in cols_in_sheet:
            errors.append(f"Source column '{col_name}' does not exist in sheet '{sheet_name}'.")
            continue

        source_col_profile = cols_in_sheet[col_name]
        detected_type = source_col_profile.detected_type

        # 3. Data type compatibility checks
        if canonical_def.expected_type == "numeric":
            if detected_type not in ("numeric", "unknown") and not source_col_profile.is_likely_metric:
                errors.append(
                    f"Type mismatch: Column '{col_name}' (detected as '{detected_type}') "
                    f"cannot be mapped to numeric field '{canonical_def.label}'."
                )

        elif (
            canonical_def.expected_type == "datetime"
            and detected_type != "datetime"
            and not source_col_profile.is_likely_date
        ):
            errors.append(
                f"Type mismatch: Column '{col_name}' (detected as '{detected_type}') "
                f"cannot be mapped to date field '{canonical_def.label}'."
            )

        # 4. Check for high null values
        if source_col_profile.null_percentage > 50.0:
            warnings.append(
                f"Warning: Column '{col_name}' mapped to '{canonical_def.label}' has {source_col_profile.null_percentage}% missing values."
            )

        # Track duplicates
        if target in mapped_targets:
            warnings.append(f"Target field '{canonical_def.label}' is mapped multiple times.")
        mapped_targets.add(target)

        src_key = (sheet_name, col_name)
        if src_key in mapped_sources:
            warnings.append(f"Source column '{col_name}' is mapped to multiple target fields.")
        mapped_sources.add(src_key)

    # 5. Check mandatory required fields
    if "order_date" not in mapped_targets:
        errors.append("Missing required field: 'Order Date' (order_date) must be mapped.")

    has_revenue = "total_revenue" in mapped_targets
    has_qty_price = "quantity" in mapped_targets and "unit_price" in mapped_targets

    if not has_revenue and not has_qty_price:
        errors.append(
            "Missing revenue data: Either 'Total Revenue' (total_revenue) or both 'Quantity' and 'Unit Price' must be mapped."
        )

    is_valid = len(errors) == 0
    return MappingValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
