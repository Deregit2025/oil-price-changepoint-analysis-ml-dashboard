"""
preprocess.py

Responsible for preparing Brent oil price data for Bayesian change point modeling.
Includes:
- Log returns calculation
- Optional aggregation (daily, weekly, monthly)
- Data validation
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class PreprocessingError(Exception):
    """Raised when preprocessing fails."""
    pass


def prepare_model_data(df: pd.DataFrame, aggregate: str = None) -> pd.DataFrame:
    """
    Prepare Brent oil price data for Bayesian change point modeling.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns 'Date' and 'Price'
    aggregate : str, optional
        Resampling frequency for aggregation:
        'D' = daily, 'W' = weekly, 'M' = monthly, None = raw data

    Returns
    -------
    pd.DataFrame
        Columns: ['Date', 'Price', 'LogReturn']
    """
    try:
        if "Date" not in df.columns or "Price" not in df.columns:
            raise PreprocessingError("Input DataFrame must contain 'Date' and 'Price'")

        model_df = df.copy()

        # Optional aggregation
        if aggregate is not None:
            model_df = model_df.set_index("Date").resample(aggregate).last().dropna().reset_index()
            logger.info("Aggregated data using '%s' frequency. New shape: %s", aggregate, model_df.shape)

        # Validate Price column
        if model_df["Price"].isna().any() or (model_df["Price"] <= 0).any():
            raise PreprocessingError("Price column contains NaN or non-positive values")

        # Compute log returns
        model_df["LogReturn"] = np.log(model_df["Price"] / model_df["Price"].shift(1))
        model_df = model_df.dropna().reset_index(drop=True)

        logger.info("Computed log returns. Final modeling dataset shape: %s", model_df.shape)
        return model_df

    except Exception:
        logger.exception("Failed preprocessing Brent oil data")
        raise
