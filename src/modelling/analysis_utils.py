# src/modelling/analysis_utils.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================
# 1. Extract the most probable change point (MAP estimate)
# ==============================
def get_change_point(trace):
    """
    Return the most probable change point (tau) from the posterior.
    
    Parameters
    ----------
    trace : arviz.InferenceData
        Posterior trace from PyMC model

    Returns
    -------
    tau_map : int
        Most probable change point index
    tau_samples : np.ndarray
        Flattened posterior samples of tau
    """
    tau_samples = trace.posterior["tau"].values.flatten()
    tau_map = int(np.median(tau_samples))  # median as MAP estimate
    return tau_map, tau_samples


# ==============================
# 2. Plot price series with change point
# ==============================
def plot_price_with_change_point(prices_df, tau, title="Brent Oil Prices with Change Point"):
    """
    Plot price series with vertical line indicating the change point.
    
    Parameters
    ----------
    prices_df : pd.DataFrame
        DataFrame with 'Date' and 'Price' columns
    tau : int
        Index of change point
    title : str
        Plot title
    """
    plt.figure(figsize=(14,5))
    plt.plot(prices_df['Date'], prices_df['Price'], label='Price', color='blue')
    plt.axvline(prices_df['Date'].iloc[tau], color='red', linestyle='--', label='Change Point')
    plt.title(title, fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.show()


# ==============================
# 3. Associate change point with detected events
# ==============================
def associate_events(prices_df, events_df, tau, window_days=5):
    """
    Find events within a window around the change point.

    Parameters
    ----------
    prices_df : pd.DataFrame
        DataFrame with 'Date' column
    events_df : pd.DataFrame
        DataFrame with 'Date' and 'Event' columns
    tau : int
        Index of change point
    window_days : int
        Number of days before and after tau to search for events

    Returns
    -------
    matched_events : pd.DataFrame
        Events near the change point
    """
    cp_date = prices_df['Date'].iloc[tau]
    start_date = cp_date - pd.Timedelta(days=window_days)
    end_date = cp_date + pd.Timedelta(days=window_days)
    
    matched_events = events_df[(events_df['Date'] >= start_date) & (events_df['Date'] <= end_date)]
    return matched_events


# ==============================
# 4. Quantify impact (mean before and after change point)
# ==============================
def quantify_impact(prices_df, tau):
    """
    Compute average price before and after the change point.

    Parameters
    ----------
    prices_df : pd.DataFrame
        DataFrame with 'Price' column
    tau : int
        Index of change point

    Returns
    -------
    impact_dict : dict
        {'before_mean': ..., 'after_mean': ..., 'change': ..., 'percent_change': ...}
    """
    before_mean = prices_df['Price'].iloc[:tau].mean()
    after_mean = prices_df['Price'].iloc[tau:].mean()
    change = after_mean - before_mean
    percent_change = (change / before_mean) * 100
    impact_dict = {
        "before_mean": before_mean,
        "after_mean": after_mean,
        "change": change,
        "percent_change": percent_change
    }
    return impact_dict


# ==============================
# 5. Summarize multiple change points
# ==============================
def summarize_change_points(prices_df, events_df, tau_list):
    """
    Summarize change points with associated events and quantified impact.

    Parameters
    ----------
    prices_df : pd.DataFrame
        DataFrame with 'Date' and 'Price' columns
    events_df : pd.DataFrame
        DataFrame with 'Date' and 'Event' columns
    tau_list : list of int
        Indices of detected change points

    Returns
    -------
    summary_df : pd.DataFrame
        DataFrame summarizing:
        - Change point date
        - Associated events
        - Mean price before and after
        - Absolute and % change
    """
    records = []
    for tau in tau_list:
        cp_date = prices_df['Date'].iloc[tau]
        matched_events = associate_events(prices_df, events_df, tau)
        impact = quantify_impact(prices_df, tau)
        
        record = {
            "ChangePointIndex": tau,
            "ChangePointDate": cp_date,
            "AssociatedEvents": ", ".join(matched_events['Event'].tolist()) if not matched_events.empty else "None",
            "PriceBefore": impact['before_mean'],
            "PriceAfter": impact['after_mean'],
            "Change": impact['change'],
            "PercentChange": impact['percent_change']
        }
        records.append(record)
    
    summary_df = pd.DataFrame.from_records(records)
    return summary_df
