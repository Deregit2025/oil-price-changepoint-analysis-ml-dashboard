import os
import logging
from typing import Optional

import numpy as np
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)


class PreprocessingError(Exception):
    """Custom exception for preprocessing failures."""
    pass


def validate_price_dataframe(df: pd.DataFrame, price_col: str) -> None:
    """
    Validate that the dataframe contains required structure.

    Raises:
        PreprocessingError: If validation fails.
    """
    if df is None or df.empty:
        raise PreprocessingError("Input dataframe is empty.")

    if price_col not in df.columns:
        raise PreprocessingError(f"Missing required column: '{price_col}'")

    if not np.issubdtype(df[price_col].dtype, np.number):
        raise PreprocessingError(f"Column '{price_col}' must be numeric.")

    if (df[price_col] <= 0).any():
        raise PreprocessingError("Price values must be positive to compute log returns.")


def compute_log_returns(
    df: pd.DataFrame,
    price_col: str = "Price",
    output_col: str = "LogReturn",
    dropna: bool = True
) -> pd.DataFrame:
    """
    Compute log returns from a price column.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing price series.
    price_col : str
        Column name for price values.
    output_col : str
        Name of output log return column.
    dropna : bool
        Whether to drop rows with NaN values after computation.

    Returns
    -------
    pd.DataFrame
        Dataframe with log return column added.
    """
    try:
        validate_price_dataframe(df, price_col)

        df = df.copy()
        df[output_col] = np.log(df[price_col] / df[price_col].shift(1))

        if dropna:
            df = df.dropna(subset=[output_col]).reset_index(drop=True)

        logging.info("Log returns computed successfully.")
        return df

    except Exception as e:
        logging.error(f"Failed to compute log returns: {e}")
        raise PreprocessingError(e)


def save_processed_data(
    df: pd.DataFrame,
    output_path: str = "../data/processed/brent_processed.csv"
) -> None:
    """
    Save processed dataframe safely to disk.
    """
    try:
        if df is None or df.empty:
            raise PreprocessingError("Cannot save empty dataframe.")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)

        logging.info(f"Processed data saved to: {output_path}")

    except Exception as e:
        logging.error(f"Failed to save processed data: {e}")
        raise PreprocessingError(e)


def preprocess_brent_prices(
    df: pd.DataFrame,
    price_col: str = "Price",
    output_path: Optional[str] = "../data/processed/brent_processed.csv"
) -> pd.DataFrame:
    """
    Full preprocessing pipeline for Brent oil prices.

    Steps:
    1. Validate data
    2. Compute log returns
    3. Save processed dataset (optional)

    Returns
    -------
    pd.DataFrame
        Processed dataframe ready for EDA and modeling.
    """
    try:
        logging.info("Starting preprocessing pipeline...")

        processed_df = compute_log_returns(df, price_col=price_col)

        if output_path:
            save_processed_data(processed_df, output_path)

        logging.info("Preprocessing completed successfully.")
        return processed_df

    except Exception as e:
        logging.error(f"Preprocessing pipeline failed: {e}")
        raise
