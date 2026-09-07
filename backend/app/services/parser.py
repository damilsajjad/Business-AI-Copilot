"""File parsing service for CSV and multi-sheet XLSX documents."""

import io
from pathlib import Path

import pandas as pd


class ParsingError(Exception):
    """Raised when file parsing fails due to format or content issues."""


def parse_csv_bytes(content: bytes, default_sheet_name: str = "Sheet1") -> dict[str, pd.DataFrame]:
    """Parse CSV content bytes into a dictionary of {sheet_name: DataFrame}."""
    if not content or len(content.strip()) == 0:
        raise ParsingError("CSV file is empty.")

    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
    delimiters = [None, ",", ";", "\t", "|"]
    df = None
    last_error = None

    for enc in encodings:
        for sep in delimiters:
            try:
                if sep is None:
                    df = pd.read_csv(
                        io.BytesIO(content),
                        encoding=enc,
                        sep=None,
                        engine="python",
                        on_bad_lines="skip",
                    )
                else:
                    df = pd.read_csv(
                        io.BytesIO(content),
                        encoding=enc,
                        sep=sep,
                        on_bad_lines="skip",
                    )
                if df is not None and not df.empty and len(df.columns) > 0:
                    break
            except Exception as e:
                last_error = e
        if df is not None and not df.empty and len(df.columns) > 0:
            break

    if df is None:
        raise ParsingError(f"Could not parse CSV file: {last_error}")

    if df.empty and len(df.columns) == 0:
        raise ParsingError("CSV contains no columns or data.")

    # Clean column headers
    df.columns = [str(col).strip() for col in df.columns]
    return {default_sheet_name: df}


def parse_xlsx_bytes(content: bytes) -> dict[str, pd.DataFrame]:
    """Parse Excel workbook bytes into a dictionary of {sheet_name: DataFrame}."""
    if not content or len(content) == 0:
        raise ParsingError("Excel file is empty.")

    try:
        excel_file = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")
        sheet_names = excel_file.sheet_names

        if not sheet_names:
            raise ParsingError("Excel workbook contains no sheets.")

        sheets_data = {}
        for sheet_name in sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # Clean column headers
            df.columns = [str(col).strip() for col in df.columns]
            sheets_data[sheet_name] = df

        return sheets_data
    except ParsingError:
        raise
    except Exception as e:
        raise ParsingError(f"Failed to parse Excel workbook: {e}") from e


def parse_file(file_name: str, content: bytes) -> dict[str, pd.DataFrame]:
    """Dispatcher to parse CSV or XLSX file bytes based on file extension."""
    suffix = Path(file_name).suffix.lower()

    if suffix == ".csv":
        return parse_csv_bytes(content)
    elif suffix in (".xlsx", ".xls"):
        return parse_xlsx_bytes(content)
    else:
        raise ParsingError(f"Unsupported file format '{suffix}'. Supported formats are .csv and .xlsx.")
