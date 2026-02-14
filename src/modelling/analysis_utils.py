"""
analysis_utils.py

Utility functions to interpret Bayesian Change Point model outputs,
compute impact metrics, and export results for dashboard/backend.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AnalysisError(Exception):
    """Raised when analysis fails"""
    pass


def build_change_point_report(df: pd.DataFrame, tau_samples: np.ndarray, trace) -> dict:
    """
    Build a summary report for the detected change point.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with 'Date', 'Price', 'LogReturn'
    tau_samples : np.ndarray
        Samples of change point index from posterior
    trace : pm.backends.base.MultiTrace
        PyMC trace

    Returns
    -------
    dict
        Report containing:
        - change_point_date
        - mean_before
        - mean_after
        - delta
        - percent_change
        - confidence (posterior probability)
    """
    try:
        if len(tau_samples) == 0:
            raise AnalysisError("tau_samples is empty")

        # MAP estimate of tau (most frequent sample)
        tau_idx = int(np.round(np.median(tau_samples)))
        tau_idx = max(0, min(tau_idx, len(df)-1))  # safety bounds

        change_date = df.iloc[tau_idx]["Date"]

        # Means before and after change point using posterior mu samples
        mu_1_samples = trace.posterior["mu_1"].values.flatten()
        mu_2_samples = trace.posterior["mu_2"].values.flatten()

        mean_before = np.mean(mu_1_samples)
        mean_after = np.mean(mu_2_samples)
        delta = mean_after - mean_before
        percent_change = (delta / abs(mean_before)) * 100 if mean_before != 0 else np.nan

        # Confidence: fraction of posterior samples where tau equals MAP
        confidence = np.mean(tau_samples == tau_idx)

        report = {
            "change_point_index": tau_idx,
            "change_point_date": change_date,
            "mean_before": mean_before,
            "mean_after": mean_after,
            "delta": delta,
            "percent_change": percent_change,
            "confidence": confidence
        }

        logger.info("Change point report generated successfully")
        return report

    except Exception:
        logger.exception("Failed building change point report")
        raise


def export_detected_event_csv(report: dict, filepath: str) -> None:
    """
    Export the detected change point report to CSV for backend/dashboard.

    Parameters
    ----------
    report : dict
        Report dictionary from build_change_point_report
    filepath : str
        Path to output CSV file
    """
    try:
        df_out = pd.DataFrame([{
            "Date": report["change_point_date"],
            "MeanBefore": report["mean_before"],
            "MeanAfter": report["mean_after"],
            "Delta": report["delta"],
            "PercentChange": report["percent_change"],
            "Confidence": report["confidence"]
        }])

        out_path = Path(filepath)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df_out.to_csv(out_path, index=False)
        logger.info("Detected event CSV exported to %s", filepath)

    except Exception:
        logger.exception("Failed exporting detected event CSV")
        raise
