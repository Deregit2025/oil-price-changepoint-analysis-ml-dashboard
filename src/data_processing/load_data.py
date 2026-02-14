"""
load_data.py

Robust loading of Brent Oil Prices CSV.
Handles mixed old (20-May-87) and modern (Apr 22, 2020) date formats.
Includes error handling and validation.
"""

import pandas as pd
import logging
from pathlib import Path

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DataValidationError(Exception):
    """Raised when CSV data is invalid."""
    pass

def load_brent_data(filepath: str) -> pd.DataFrame:
    """
    Load Brent oil prices CSV with robust date parsing for mixed formats.

    Parameters
    ----------
    filepath : str
        Path to BrentOilPrices.csv

    Returns
    -------
    pd.DataFrame
        Columns: ['Date', 'Price'], sorted by date ascending
    """
    try:
        file_path_obj = Path(filepath)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Load CSV
        df = pd.read_csv(filepath)

        # Strip whitespace from column names
        df.columns = df.columns.str.strip()

        # Validate required columns
        if "Date" not in df.columns or "Price" not in df.columns:
            raise DataValidationError("CSV must contain 'Date' and 'Price' columns")

        # Strip whitespace from Date column
        df["Date"] = df["Date"].astype(str).str.strip()

        # -----------------------------
        # Flexible date parsing ONLY
        # -----------------------------
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)

        # Check for invalid dates
        if df["Date"].isna().any():
            invalid_rows = df[df["Date"].isna()]
            raise DataValidationError(
                f"Invalid date format detected in the following rows:\n{invalid_rows}"
            )

        # Convert Price to numeric
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
        if df["Price"].isna().any():
            invalid_prices = df[df["Price"].isna()]
            raise DataValidationError(
                f"Invalid Price values detected in the following rows:\n{invalid_prices}"
            )

        # Sort by date ascending
        df = df.sort_values("Date").reset_index(drop=True)

        logger.info("Loaded Brent dataset with %d rows", len(df))
        return df

    except Exception as e:
        logger.exception("Failed to load Brent oil data")
        raise
