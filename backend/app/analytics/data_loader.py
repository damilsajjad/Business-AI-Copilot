"""Canonical dataset normalization from mapped raw files."""

from typing import Any

import pandas as pd

from app.schemas.mapping import ColumnMappingItem
from app.services.parser import parse_file
from app.services.storage import storage_service


def normalize_canonical_dataframe(
    raw_sheets: dict[str, pd.DataFrame],
    mappings: list[ColumnMappingItem] | list[dict[str, Any]],
) -> pd.DataFrame:
    """Transform raw sheets into a single typed canonical DataFrame using confirmed mappings."""
    # Convert mapping list to dict for fast lookup: target_field -> (sheet, column)
    mapping_dict = {}
    for m in mappings:
        if isinstance(m, dict):
            target = m["target_field"]
            sheet = m.get("source_sheet", "Sheet1")
            col = m["source_column"]
        else:
            target = m.target_field
            sheet = m.source_sheet
            col = m.source_column

        # Fallback to first available sheet if not found
        if sheet not in raw_sheets and raw_sheets:
            sheet = list(raw_sheets.keys())[0]

        mapping_dict[target] = (sheet, col)

    if not raw_sheets:
        return pd.DataFrame()

    canonical_cols: dict[str, Any] = {}

    for target_field, (sheet_name, col_name) in mapping_dict.items():
        if sheet_name in raw_sheets and col_name in raw_sheets[sheet_name].columns:
            series = raw_sheets[sheet_name][col_name]
            canonical_cols[target_field] = series

    df = pd.DataFrame(canonical_cols)

    # 1. Parse order_date
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    else:
        # Fallback if no order_date
        df["order_date"] = pd.NaT

    # 2. Parse numerical metrics
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)
    else:
        df["quantity"] = 1

    if "unit_price" in df.columns:
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
    else:
        df["unit_price"] = 0.0

    if "total_revenue" in df.columns:
        df["total_revenue"] = pd.to_numeric(df["total_revenue"], errors="coerce").fillna(0.0)
    elif "quantity" in df.columns and "unit_price" in df.columns:
        df["total_revenue"] = (df["quantity"] * df["unit_price"]).round(2)
    else:
        df["total_revenue"] = 0.0

    if "discount_rate" in df.columns:
        df["discount_rate"] = pd.to_numeric(df["discount_rate"], errors="coerce").fillna(0.0)
    else:
        df["discount_rate"] = 0.0

    # 3. Categorical & identifiers
    if "product_name" not in df.columns and "product_id" in df.columns:
        df["product_name"] = df["product_id"].astype(str)
    elif "product_name" not in df.columns:
        df["product_name"] = "General Product"
    else:
        df["product_name"] = df["product_name"].astype(str).fillna("General Product")

    if "product_id" not in df.columns:
        df["product_id"] = df["product_name"].astype(str)

    if "category" not in df.columns:
        df["category"] = "General"
    else:
        df["category"] = df["category"].astype(str).fillna("General")

    if "customer_id" in df.columns:
        df["customer_id"] = df["customer_id"].astype(str).fillna("Unknown Customer")

    if "order_id" not in df.columns:
        df["order_id"] = [f"ORD-{i+1:05d}" for i in range(len(df))]
    else:
        df["order_id"] = df["order_id"].astype(str)

    if "sales_channel" not in df.columns:
        df["sales_channel"] = "Direct"
    else:
        df["sales_channel"] = df["sales_channel"].astype(str).fillna("Direct")

    # Filter out rows with invalid date or negative/null revenue
    valid_mask = df["order_date"].notna() & df["total_revenue"].notna()
    df = df[valid_mask].copy()

    # Chronological sort
    df = df.sort_values(by="order_date").reset_index(drop=True)

    return df


def load_canonical_data_from_file(
    storage_path: str,
    original_filename: str,
    mappings: list[ColumnMappingItem] | list[dict[str, Any]],
) -> pd.DataFrame:
    """Read raw file from storage and return normalized canonical DataFrame."""
    content = storage_service.read_file(storage_path)
    sheets = parse_file(original_filename, content)
    return normalize_canonical_dataframe(sheets, mappings)
