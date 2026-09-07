"""Tests for deterministic data profiler and semantic tag inference."""

import pandas as pd

from app.data.synthetic_data import generate_retail_dataset
from app.services.profiler import profile_dataset, profile_sheet


def test_profile_retail_dataset():
    """Profile generated retail dataset and verify computed metrics."""
    df = generate_retail_dataset(num_orders=100)
    sheets_dict = {"Orders": df}

    result = profile_dataset(
        file_id="test-file-123",
        file_name="retail_orders.csv",
        sheets_dict=sheets_dict,
    )

    assert result.file_id == "test-file-123"
    assert result.total_sheets == 1
    assert result.data_quality_score > 80.0

    sheet = result.sheets[0]
    assert sheet.sheet_name == "Orders"
    assert sheet.row_count == 100
    assert sheet.column_count == 11

    col_map = {col.name: col for col in sheet.columns}

    # Verify ID inference
    assert col_map["order_id"].is_likely_id is True
    assert col_map["customer_id"].is_likely_id is True

    # Verify Metric inference
    assert col_map["total_revenue"].is_likely_metric is True
    assert col_map["quantity"].is_likely_metric is True
    assert col_map["total_revenue"].stats is not None
    assert col_map["total_revenue"].stats.min is not None
    assert col_map["total_revenue"].stats.max is not None

    # Verify Date inference
    assert col_map["order_date"].is_likely_date is True
    assert col_map["order_date"].detected_type == "datetime"

    # Verify Dimension inference
    assert col_map["category"].is_likely_dimension is True
    assert col_map["sales_channel"].is_likely_dimension is True


def test_profile_sheet_with_empty_and_duplicate_data():
    """Empty columns and duplicates should generate proper warnings and lower quality score."""
    df = pd.DataFrame({
        "id": [1, 2, 2, 4],
        "empty_col": [None, None, None, None],
        "val": [10.0, 20.0, 20.0, 40.0],
    })

    sheet = profile_sheet("TestSheet", df)
    assert sheet.row_count == 4
    assert sheet.duplicate_rows_count == 1

    col_map = {col.name: col for col in sheet.columns}
    assert col_map["empty_col"].null_percentage == 100.0
    assert any("empty" in w.lower() for w in col_map["empty_col"].warnings)
