from pathlib import Path
from typing import Union

import pandas as pd


# =========================
# Configuration
# =========================

RAW_DATA_PATH = Path("data/raw/BrentOilPrices.csv")
PROCESSED_EVENTS_PATH = Path("data/processed/detected_events.csv")

REQUIRED_PRICE_COLUMNS = {"Date", "Price"}
REQUIRED_EVENT_COLUMNS = {"Date", "Event", "Category"}


# =========================
# Utility Validators
# =========================

def _validate_file_exists(file_path: Path) -> None:
    """Ensure the provided file path exists."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")


def _validate_columns(df: pd.DataFrame, required_columns: set, dataset_name: str) -> None:
    """Ensure required columns exist in DataFrame."""
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"{dataset_name} is missing required columns: {missing}"
        )


def _parse_date_column(df: pd.DataFrame, column_name: str = "Date") -> pd.DataFrame:
    """Convert Date column to datetime safely."""
    try:
        df[column_name] = pd.to_datetime(df[column_name], dayfirst=True, errors="raise")
    except Exception as exc:
        raise ValueError(f"Failed to parse '{column_name}' column to datetime.") from exc
    return df


# =========================
# Public Loaders
# =========================

def load_brent_prices(file_path: Union[str, Path] = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Load and validate Brent oil price dataset.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame sorted by date.
    """
    path = Path(file_path)

    _validate_file_exists(path)

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise IOError(f"Failed to read Brent price data from {path}") from exc

    _validate_columns(df, REQUIRED_PRICE_COLUMNS, "Brent price dataset")

    df = _parse_date_column(df, "Date")

    # Validate numeric price
    if not pd.api.types.is_numeric_dtype(df["Price"]):
        raise TypeError("Price column must be numeric.")

    if df["Price"].isna().any():
        raise ValueError("Price column contains missing values.")

    df = df.sort_values("Date").reset_index(drop=True)

    return df


def load_detected_events(file_path: Union[str, Path] = PROCESSED_EVENTS_PATH) -> pd.DataFrame:
    """
    Load and validate detected major events dataset.

    Returns
    -------
    pd.DataFrame
        Cleaned event DataFrame sorted by date.
    """
    path = Path(file_path)

    _validate_file_exists(path)

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise IOError(f"Failed to read detected events from {path}") from exc

    _validate_columns(df, REQUIRED_EVENT_COLUMNS, "Event dataset")

    df = _parse_date_column(df, "Date")

    if df["Date"].isna().any():
        raise ValueError("Event dataset contains invalid dates.")

    df = df.sort_values("Date").reset_index(drop=True)

    return df
