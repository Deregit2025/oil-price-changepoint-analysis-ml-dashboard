# tests/test_data_loading.py
"""
Pytest suite for Brent oil data loading (src.data_processing.load_data).
"""

import pytest
import pandas as pd
from pathlib import Path

from src.data_processing.load_data import load_brent_data, DataValidationError


# ---------------------------------------------------------------------------
# Test: valid CSV
# ---------------------------------------------------------------------------

def test_load_valid_csv(tmp_path):
    """Valid CSV with Date and Price loads to DataFrame with correct dtypes."""
    csv_path = tmp_path / "valid.csv"
    csv_path.write_text("Date,Price\n20-May-87,18.63\n21-May-87,18.45\n")
    df = load_brent_data(str(csv_path))
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["Date", "Price"]
    assert len(df) == 2
    assert pd.api.types.is_datetime64_any_dtype(df["Date"])
    assert pd.api.types.is_float_dtype(df["Price"])
    assert df["Price"].iloc[0] == 18.63
    assert df["Price"].iloc[1] == 18.45


def test_load_valid_csv_mixed_date_formats(tmp_path):
    """Mixed date formats (e.g. 20-May-87 and 2020-04-22) parse correctly."""
    csv_path = tmp_path / "mixed_dates.csv"
    csv_path.write_text(
        "Date,Price\n"
        "20-May-87,18.63\n"
        "22-Apr-2020,19.50\n"
        "2020-04-23,20.10\n"
    )
    df = load_brent_data(str(csv_path))
    assert len(df) == 3
    assert pd.api.types.is_datetime64_any_dtype(df["Date"])
    assert df["Date"].iloc[0] < df["Date"].iloc[1] < df["Date"].iloc[2]
    assert df["Price"].tolist() == [18.63, 19.50, 20.10]


def test_load_valid_csv_sorted_ascending(tmp_path):
    """Output is sorted by Date ascending regardless of CSV row order."""
    csv_path = tmp_path / "unsorted.csv"
    csv_path.write_text(
        "Date,Price\n"
        "21-May-87,18.45\n"
        "20-May-87,18.63\n"
        "22-May-87,18.55\n"
    )
    df = load_brent_data(str(csv_path))
    assert df["Date"].is_monotonic_increasing
    assert df["Date"].iloc[0].strftime("%Y-%m-%d") == "1987-05-20"
    assert df["Date"].iloc[-1].strftime("%Y-%m-%d") == "1987-05-22"


def test_load_valid_csv_whitespace_columns(tmp_path):
    """Whitespace in column names and in Date values is stripped."""
    csv_path = tmp_path / "whitespace.csv"
    csv_path.write_text("  Date  ,  Price  \n  20-May-87  ,  18.63  \n")
    df = load_brent_data(str(csv_path))
    assert list(df.columns) == ["Date", "Price"]
    assert len(df) == 1
    assert df["Price"].iloc[0] == 18.63


# ---------------------------------------------------------------------------
# Test: file not found
# ---------------------------------------------------------------------------

def test_file_not_found(tmp_path):
    """FileNotFoundError is raised when the file path does not exist."""
    missing_path = tmp_path / "does_not_exist.csv"
    assert not missing_path.exists()
    with pytest.raises(FileNotFoundError) as exc_info:
        load_brent_data(str(missing_path))
    assert "File not found" in str(exc_info.value) or "does_not_exist" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Test: validation errors
# ---------------------------------------------------------------------------

def test_missing_columns(tmp_path):
    """CSV without 'Date' or 'Price' raises DataValidationError."""
    csv_path = tmp_path / "missing_cols.csv"
    csv_path.write_text("Timestamp,Value\n20-May-87,18.63\n")
    with pytest.raises(DataValidationError) as exc_info:
        load_brent_data(str(csv_path))
    assert "Date" in str(exc_info.value) and "Price" in str(exc_info.value)


def test_missing_date_column_only(tmp_path):
    """CSV with Price but no Date raises DataValidationError."""
    csv_path = tmp_path / "no_date.csv"
    csv_path.write_text("Price\n18.63\n")
    with pytest.raises(DataValidationError):
        load_brent_data(str(csv_path))


def test_invalid_date(tmp_path):
    """Unparseable date values raise DataValidationError."""
    csv_path = tmp_path / "invalid_date.csv"
    csv_path.write_text("Date,Price\nnot_a_date,18.63\n")
    with pytest.raises(DataValidationError) as exc_info:
        load_brent_data(str(csv_path))
    assert "Invalid date" in str(exc_info.value) or "date" in str(exc_info.value).lower()


def test_invalid_price(tmp_path):
    """Non-numeric Price values raise DataValidationError."""
    csv_path = tmp_path / "invalid_price.csv"
    csv_path.write_text("Date,Price\n20-May-87,not_a_number\n")
    with pytest.raises(DataValidationError) as exc_info:
        load_brent_data(str(csv_path))
    assert "Price" in str(exc_info.value) or "Invalid" in str(exc_info.value)


def test_price_with_empty_cell(tmp_path):
    """Empty or missing Price cell raises DataValidationError."""
    csv_path = tmp_path / "empty_price.csv"
    csv_path.write_text("Date,Price\n20-May-87,\n")
    with pytest.raises(DataValidationError):
        load_brent_data(str(csv_path))
