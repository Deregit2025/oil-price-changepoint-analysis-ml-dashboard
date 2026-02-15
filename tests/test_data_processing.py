# tests/test_data_processing.py
"""
Pytest suite for Brent oil data preprocessing (src.data_processing.preprocess).
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.data_processing.preprocess import prepare_model_data, PreprocessingError


def _make_price_df(dates, prices):
    """Helper: DataFrame with Date and Price."""
    return pd.DataFrame({"Date": dates, "Price": prices})


# ---------------------------------------------------------------------------
# Test: valid input, no aggregation
# ---------------------------------------------------------------------------

def test_prepare_model_data_returns_date_price_logreturn():
    """Output has columns Date, Price, LogReturn."""
    df = _make_price_df(
        [datetime(2020, 1, 1), datetime(2020, 1, 2), datetime(2020, 1, 3)],
        [100.0, 102.0, 101.0],
    )
    result = prepare_model_data(df)
    assert list(result.columns) == ["Date", "Price", "LogReturn"]
    assert len(result) == 2  # first row dropped (no prior for log return)


def test_prepare_model_data_logreturn_formula():
    """LogReturn equals log(Price / Price_prev)."""
    df = _make_price_df(
        [datetime(2020, 1, 1), datetime(2020, 1, 2), datetime(2020, 1, 3)],
        [100.0, 102.0, 101.0],
    )
    result = prepare_model_data(df)
    # Row 0: log(102/100) ≈ 0.0198
    np.testing.assert_allclose(result["LogReturn"].iloc[0], np.log(102.0 / 100.0))
    # Row 1: log(101/102) ≈ -0.0099
    np.testing.assert_allclose(result["LogReturn"].iloc[1], np.log(101.0 / 102.0))


def test_prepare_model_data_preserves_dates_and_prices():
    """Date and Price in output match input (excluding first row)."""
    dates = [datetime(2020, 1, 1), datetime(2020, 1, 2), datetime(2020, 1, 3)]
    prices = [100.0, 102.0, 101.0]
    df = _make_price_df(dates, prices)
    result = prepare_model_data(df)
    assert result["Date"].tolist() == [dates[1], dates[2]]
    assert result["Price"].tolist() == [102.0, 101.0]


def test_prepare_model_data_single_row_dropped():
    """With only two rows, one log return row remains."""
    df = _make_price_df([datetime(2020, 1, 1), datetime(2020, 1, 2)], [100.0, 105.0])
    result = prepare_model_data(df)
    assert len(result) == 1
    np.testing.assert_allclose(result["LogReturn"].iloc[0], np.log(1.05))


# ---------------------------------------------------------------------------
# Test: valid input with aggregation
# ---------------------------------------------------------------------------

def test_prepare_model_data_weekly_aggregation():
    """aggregate='W' resamples to weekly and then computes log returns."""
    base = datetime(2020, 1, 1)
    dates = [base + timedelta(days=i) for i in range(14)]
    prices = [100.0 + i for i in range(14)]  # 100..113
    df = _make_price_df(dates, prices)
    result = prepare_model_data(df, aggregate="W")
    assert "LogReturn" in result.columns
    assert len(result) >= 1
    # All rows should have finite LogReturn (first aggregated row dropped)
    assert result["LogReturn"].notna().all()
    assert (result["Price"] >= 100).all() and (result["Price"] <= 113).all()


def test_prepare_model_data_monthly_aggregation():
    """aggregate='M' resamples to month-end and computes log returns."""
    dates = [
        datetime(2020, 1, 15),
        datetime(2020, 2, 10),
        datetime(2020, 3, 20),
    ]
    prices = [50.0, 52.0, 51.0]
    df = _make_price_df(dates, prices)
    result = prepare_model_data(df, aggregate="M")
    assert "LogReturn" in result.columns
    assert len(result) == 2  # 3 months → 3 rows, 2 log returns


def test_prepare_model_data_aggregate_none_same_as_omit():
    """aggregate=None gives same result as not passing aggregate."""
    df = _make_price_df(
        [datetime(2020, 1, 1), datetime(2020, 1, 2), datetime(2020, 1, 3)],
        [10.0, 11.0, 10.5],
    )
    r1 = prepare_model_data(df, aggregate=None)
    r2 = prepare_model_data(df)
    pd.testing.assert_frame_equal(r1, r2)


# ---------------------------------------------------------------------------
# Test: validation errors
# ---------------------------------------------------------------------------

def test_prepare_model_data_missing_date_column():
    """DataFrame without 'Date' raises PreprocessingError."""
    df = pd.DataFrame({"Price": [100.0, 101.0]})
    with pytest.raises(PreprocessingError) as exc_info:
        prepare_model_data(df)
    assert "Date" in str(exc_info.value)


def test_prepare_model_data_missing_price_column():
    """DataFrame without 'Price' raises PreprocessingError."""
    df = pd.DataFrame({"Date": [datetime(2020, 1, 1), datetime(2020, 1, 2)]})
    with pytest.raises(PreprocessingError) as exc_info:
        prepare_model_data(df)
    assert "Price" in str(exc_info.value)


def test_prepare_model_data_nan_price():
    """NaN in Price raises PreprocessingError."""
    df = _make_price_df(
        [datetime(2020, 1, 1), datetime(2020, 1, 2), datetime(2020, 1, 3)],
        [100.0, np.nan, 102.0],
    )
    with pytest.raises(PreprocessingError) as exc_info:
        prepare_model_data(df)
    assert "NaN" in str(exc_info.value) or "Price" in str(exc_info.value)


def test_prepare_model_data_zero_price():
    """Zero in Price raises PreprocessingError (log undefined)."""
    df = _make_price_df(
        [datetime(2020, 1, 1), datetime(2020, 1, 2)],
        [100.0, 0.0],
    )
    with pytest.raises(PreprocessingError) as exc_info:
        prepare_model_data(df)
    assert "non-positive" in str(exc_info.value).lower() or "Price" in str(exc_info.value)


def test_prepare_model_data_negative_price():
    """Negative Price raises PreprocessingError."""
    df = _make_price_df(
        [datetime(2020, 1, 1), datetime(2020, 1, 2)],
        [100.0, -50.0],
    )
    with pytest.raises(PreprocessingError):
        prepare_model_data(df)


# ---------------------------------------------------------------------------
# Test: input not modified
# ---------------------------------------------------------------------------

def test_prepare_model_data_does_not_mutate_input():
    """Input DataFrame is not modified in place."""
    df = _make_price_df(
        [datetime(2020, 1, 1), datetime(2020, 1, 2)],
        [100.0, 105.0],
    )
    original_len = len(df)
    original_cols = list(df.columns)
    prepare_model_data(df)
    assert len(df) == original_len
    assert list(df.columns) == original_cols
    assert "LogReturn" not in df.columns
