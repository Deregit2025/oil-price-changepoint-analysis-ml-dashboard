import os
import pandas as pd


def _validate_file_path(file_path: str) -> None:
    """Check if the file exists."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")


def _validate_columns(df: pd.DataFrame, required_columns: list) -> None:
    """Ensure required columns exist in dataframe."""
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def load_brent_prices(file_path: str = "../data/raw/BrentOilPrices.csv") -> pd.DataFrame:
    """
    Load Brent oil price dataset with validation and cleaning.
    """

    _validate_file_path(file_path)

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

    _validate_columns(df, ["Date", "Price"])

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    if df["Date"].isnull().any():
        raise ValueError("Invalid date values detected.")

    df = df.sort_values("Date").reset_index(drop=True)

    return df


def load_detected_events(file_path: str = "../data/processed/detected_events.csv") -> pd.DataFrame:
    """
    Load detected market events dataset with validation.
    """

    _validate_file_path(file_path)

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

    _validate_columns(df, ["Date"])

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    if df["Date"].isnull().any():
        raise ValueError("Invalid event dates detected.")

    df = df.sort_values("Date").reset_index(drop=True)

    return df
