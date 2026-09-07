"""Tests for CSV and XLSX file parsing service."""

import pandas as pd
import pytest

from app.data.synthetic_data import (
    generate_multi_sheet_xlsx_bytes,
    generate_retail_csv_bytes,
)
from app.services.parser import ParsingError, parse_file


def test_parse_valid_csv():
    """Valid CSV content should be parsed into a single-sheet dictionary of DataFrames."""
    csv_bytes = generate_retail_csv_bytes(num_orders=50)
    sheets = parse_file("sales_data.csv", csv_bytes)

    assert "Sheet1" in sheets
    df = sheets["Sheet1"]
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 50
    assert "order_id" in df.columns
    assert "total_revenue" in df.columns


def test_parse_valid_xlsx_multi_sheet():
    """Valid multi-sheet XLSX should extract each worksheet independently."""
    xlsx_bytes = generate_multi_sheet_xlsx_bytes(num_orders=30)
    sheets = parse_file("sales_workbook.xlsx", xlsx_bytes)

    assert "Transactions" in sheets
    assert "Products" in sheets
    assert len(sheets["Transactions"]) == 30
    assert len(sheets["Products"]) > 0


def test_parse_empty_csv_raises_error():
    """Empty CSV should raise ParsingError."""
    with pytest.raises(ParsingError, match="empty"):
        parse_file("empty.csv", b"")


def test_parse_unsupported_format_raises_error():
    """Unsupported file extension should raise ParsingError."""
    with pytest.raises(ParsingError, match="Unsupported file format"):
        parse_file("data.json", b'{"key": "value"}')


def test_parse_corrupted_xlsx_raises_error():
    """Corrupted binary data with .xlsx extension should raise ParsingError."""
    with pytest.raises(ParsingError):
        parse_file("corrupted.xlsx", b"NOT_A_REAL_ZIP_EXCEL_FILE")
