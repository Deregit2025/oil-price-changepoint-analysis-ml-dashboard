import numpy as np
import pandas as pd


def compute_log_returns(df: pd.DataFrame, price_col: str = "Price") -> pd.DataFrame:
    """
    Compute log returns from a price series with validation.
    """

    if df is None or df.empty:
        raise ValueError("Input dataframe is empty.")

    if price_col not in df.columns:
        raise ValueError(f"Column '{price_col}' not found in dataframe.")

    if (df[price_col] <= 0).any():
        raise ValueError("Price values must be positive to compute log returns.")

    df = df.copy()
    df["LogReturn"] = np.log(df[price_col] / df[price_col].shift(1))
    df = df.dropna().reset_index(drop=True)

    return df
