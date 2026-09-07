"""Tests for deterministic column mapping validator."""

from app.data.synthetic_data import generate_retail_dataset
from app.schemas.mapping import ColumnMappingItem
from app.services.mapping_validator import validate_mapping
from app.services.profiler import profile_dataset


def test_valid_mapping_passes():
    """A complete and type-compatible mapping should pass validation with is_valid=True."""
    df = generate_retail_dataset(num_orders=50)
    profile = profile_dataset(file_id="f1", file_name="sales.csv", sheets_dict={"Sheet1": df})

    valid_mappings = [
        ColumnMappingItem(target_field="order_id", source_sheet="Sheet1", source_column="order_id"),
        ColumnMappingItem(target_field="order_date", source_sheet="Sheet1", source_column="order_date"),
        ColumnMappingItem(target_field="customer_id", source_sheet="Sheet1", source_column="customer_id"),
        ColumnMappingItem(target_field="product_name", source_sheet="Sheet1", source_column="product_name"),
        ColumnMappingItem(target_field="total_revenue", source_sheet="Sheet1", source_column="total_revenue"),
        ColumnMappingItem(target_field="quantity", source_sheet="Sheet1", source_column="quantity"),
    ]

    result = validate_mapping(valid_mappings, profile)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_missing_required_date_fails():
    """Omitting order_date must fail validation."""
    df = generate_retail_dataset(num_orders=50)
    profile = profile_dataset(file_id="f1", file_name="sales.csv", sheets_dict={"Sheet1": df})

    mappings_no_date = [
        ColumnMappingItem(target_field="total_revenue", source_sheet="Sheet1", source_column="total_revenue"),
    ]

    result = validate_mapping(mappings_no_date, profile)
    assert result.is_valid is False
    assert any("order_date" in err for err in result.errors)


def test_incompatible_type_mapping_fails():
    """Mapping a non-numeric text column (e.g. product_name) to total_revenue must fail."""
    df = generate_retail_dataset(num_orders=50)
    profile = profile_dataset(file_id="f1", file_name="sales.csv", sheets_dict={"Sheet1": df})

    invalid_type_mappings = [
        ColumnMappingItem(target_field="order_date", source_sheet="Sheet1", source_column="order_date"),
        ColumnMappingItem(target_field="total_revenue", source_sheet="Sheet1", source_column="product_name"),
    ]

    result = validate_mapping(invalid_type_mappings, profile)
    assert result.is_valid is False
    assert any("cannot be mapped to numeric field" in err for err in result.errors)


def test_nonexistent_column_fails():
    """Mapping a column that does not exist in the source sheet must fail."""
    df = generate_retail_dataset(num_orders=50)
    profile = profile_dataset(file_id="f1", file_name="sales.csv", sheets_dict={"Sheet1": df})

    fake_col_mappings = [
        ColumnMappingItem(target_field="order_date", source_sheet="Sheet1", source_column="non_existent_col"),
        ColumnMappingItem(target_field="total_revenue", source_sheet="Sheet1", source_column="total_revenue"),
    ]

    result = validate_mapping(fake_col_mappings, profile)
    assert result.is_valid is False
    assert any("does not exist" in err for err in result.errors)
