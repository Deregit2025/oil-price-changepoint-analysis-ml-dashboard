# tests/test_modelling.py
"""
Pytest suite for Bayesian change point model and analysis utils
(src.modelling.bayesian_cp_model, src.modelling.analysis_utils).
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

from src.modelling.analysis_utils import (
    build_change_point_report,
    export_detected_event_csv,
    AnalysisError,
)


# ---------------------------------------------------------------------------
# Mock trace for testing build_change_point_report (avoids slow MCMC)
# ---------------------------------------------------------------------------

class _MockVar:
    """Minimal mock for PyMC trace posterior variable (.values.flatten())."""
    def __init__(self, data):
        self._data = np.asarray(data)

    @property
    def values(self):
        return self._data

    def flatten(self):
        return self._data.flatten()


def _make_mock_trace(mu_1_values, mu_2_values):
    """Build an object that quacks like a PyMC trace for posterior["mu_1"], ["mu_2"]."""
    class MockTrace:
        posterior = {
            "mu_1": _MockVar(mu_1_values),
            "mu_2": _MockVar(mu_2_values),
        }
    return MockTrace()


# ---------------------------------------------------------------------------
# Tests: build_change_point_report
# ---------------------------------------------------------------------------

def test_build_change_point_report_returns_expected_keys():
    """Report dict contains change_point_index, change_point_date, mean_before, mean_after, delta, percent_change, confidence."""
    n = 10
    df = pd.DataFrame({
        "Date": pd.date_range("2020-01-01", periods=n, freq="D"),
        "Price": np.linspace(100, 110, n),
        "LogReturn": np.random.randn(n) * 0.01,
    })
    tau_samples = np.array([3] * 50)  # median 3
    trace = _make_mock_trace(np.ones(50) * 0.01, np.ones(50) * 0.02)
    report = build_change_point_report(df, tau_samples, trace)
    expected_keys = {
        "change_point_index", "change_point_date", "mean_before", "mean_after",
        "delta", "percent_change", "confidence",
    }
    assert expected_keys.issubset(report.keys())


def test_build_change_point_report_uses_median_tau():
    """change_point_index is the median of tau_samples (clamped to valid index)."""
    n = 20
    df = pd.DataFrame({
        "Date": pd.date_range("2020-01-01", periods=n, freq="D"),
        "Price": np.linspace(100, 120, n),
        "LogReturn": np.random.randn(n) * 0.01,
    })
    tau_samples = np.array([7] * 100)
    trace = _make_mock_trace(np.zeros(100), np.zeros(100))
    report = build_change_point_report(df, tau_samples, trace)
    assert report["change_point_index"] == 7
    assert report["change_point_date"] == df.iloc[7]["Date"]


def test_build_change_point_report_clamps_tau_to_bounds():
    """If median of tau_samples is out of range, index is clamped to [0, len(df)-1]."""
    n = 5
    df = pd.DataFrame({
        "Date": pd.date_range("2020-01-01", periods=n, freq="D"),
        "Price": np.linspace(100, 104, n),
        "LogReturn": np.random.randn(n) * 0.01,
    })
    tau_samples = np.array([100] * 50)  # way past end
    trace = _make_mock_trace(np.zeros(50), np.zeros(50))
    report = build_change_point_report(df, tau_samples, trace)
    assert report["change_point_index"] == n - 1


def test_build_change_point_report_mean_before_after_delta():
    """mean_before, mean_after and delta are computed from trace posteriors."""
    n = 10
    df = pd.DataFrame({
        "Date": pd.date_range("2020-01-01", periods=n, freq="D"),
        "Price": np.linspace(100, 109, n),
        "LogReturn": np.random.randn(n) * 0.01,
    })
    tau_samples = np.array([4] * 100)
    trace = _make_mock_trace(np.ones(100) * 0.01, np.ones(100) * 0.03)
    report = build_change_point_report(df, tau_samples, trace)
    assert report["mean_before"] == 0.01
    assert report["mean_after"] == 0.03
    assert report["delta"] == pytest.approx(0.02)


def test_build_change_point_report_confidence_between_0_and_1():
    """confidence is the fraction of tau_samples equal to change_point_index."""
    n = 10
    df = pd.DataFrame({
        "Date": pd.date_range("2020-01-01", periods=n, freq="D"),
        "Price": np.linspace(100, 109, n),
        "LogReturn": np.random.randn(n) * 0.01,
    })
    tau_samples = np.array([2] * 80 + [3] * 20)  # 80% at 2
    trace = _make_mock_trace(np.zeros(100), np.zeros(100))
    report = build_change_point_report(df, tau_samples, trace)
    assert 0 <= report["confidence"] <= 1
    assert report["confidence"] == pytest.approx(0.8)


def test_build_change_point_report_empty_tau_samples_raises():
    """Empty tau_samples raises AnalysisError."""
    df = pd.DataFrame({
        "Date": [datetime(2020, 1, 1)],
        "Price": [100.0],
        "LogReturn": [0.0],
    })
    trace = _make_mock_trace(np.array([0.0]), np.array([0.0]))
    with pytest.raises(AnalysisError) as exc_info:
        build_change_point_report(df, np.array([]), trace)
    assert "tau_samples" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()


def test_build_change_point_report_percent_change_when_mean_before_zero():
    """When mean_before is 0, percent_change is NaN (avoid div by zero)."""
    n = 10
    df = pd.DataFrame({
        "Date": pd.date_range("2020-01-01", periods=n, freq="D"),
        "Price": np.linspace(100, 109, n),
        "LogReturn": np.random.randn(n) * 0.01,
    })
    tau_samples = np.array([5] * 100)
    trace = _make_mock_trace(np.zeros(100), np.ones(100) * 0.02)
    report = build_change_point_report(df, tau_samples, trace)
    assert report["mean_before"] == 0.0
    assert np.isnan(report["percent_change"])


# ---------------------------------------------------------------------------
# Tests: export_detected_event_csv
# ---------------------------------------------------------------------------

def test_export_detected_event_csv_creates_file(tmp_path):
    """export_detected_event_csv writes a CSV at the given path."""
    report = {
        "change_point_index": 5,
        "change_point_date": datetime(2020, 6, 15),
        "mean_before": 0.01,
        "mean_after": 0.02,
        "delta": 0.01,
        "percent_change": 100.0,
        "confidence": 0.85,
    }
    out_path = tmp_path / "detected_events.csv"
    export_detected_event_csv(report, str(out_path))
    assert out_path.exists()
    assert out_path.read_text()


def test_export_detected_event_csv_has_expected_columns(tmp_path):
    """Exported CSV has Date, MeanBefore, MeanAfter, Delta, PercentChange, Confidence."""
    report = {
        "change_point_index": 0,
        "change_point_date": datetime(2020, 1, 1),
        "mean_before": 0.0,
        "mean_after": 0.01,
        "delta": 0.01,
        "percent_change": 50.0,
        "confidence": 0.9,
    }
    out_path = tmp_path / "events.csv"
    export_detected_event_csv(report, str(out_path))
    df = pd.read_csv(out_path)
    expected = {"Date", "MeanBefore", "MeanAfter", "Delta", "PercentChange", "Confidence"}
    assert expected.issubset(df.columns)


def test_export_detected_event_csv_content_matches_report(tmp_path):
    """Single row content matches the report values."""
    report = {
        "change_point_index": 3,
        "change_point_date": datetime(2020, 3, 10),
        "mean_before": -0.005,
        "mean_after": 0.008,
        "delta": 0.013,
        "percent_change": -260.0,
        "confidence": 0.75,
    }
    out_path = tmp_path / "out.csv"
    export_detected_event_csv(report, str(out_path))
    df = pd.read_csv(out_path)
    assert len(df) == 1
    assert df["MeanBefore"].iloc[0] == pytest.approx(report["mean_before"])
    assert df["MeanAfter"].iloc[0] == pytest.approx(report["mean_after"])
    assert df["Delta"].iloc[0] == pytest.approx(report["delta"])
    assert df["PercentChange"].iloc[0] == pytest.approx(report["percent_change"])
    assert df["Confidence"].iloc[0] == pytest.approx(report["confidence"])


def test_export_detected_event_csv_creates_parent_dirs(tmp_path):
    """Parent directories are created if they do not exist."""
    report = {
        "change_point_index": 0,
        "change_point_date": datetime(2020, 1, 1),
        "mean_before": 0.0,
        "mean_after": 0.0,
        "delta": 0.0,
        "percent_change": 0.0,
        "confidence": 1.0,
    }
    out_path = tmp_path / "subdir" / "nested" / "events.csv"
    export_detected_event_csv(report, str(out_path))
    assert out_path.exists()


# ---------------------------------------------------------------------------
# Tests: run_bayesian_change_point_model (optional; can be slow)
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_run_bayesian_change_point_model_returns_expected_structure():
    """run_bayesian_change_point_model returns dict with trace, summary, tau_posterior."""
    pytest.importorskip("pymc")
    from src.modelling.bayesian_cp_model import run_bayesian_change_point_model

    np.random.seed(42)
    n = 30
    log_returns = np.random.randn(n).astype(np.float64) * 0.02

    result = run_bayesian_change_point_model(
        log_returns,
        draws=50,
        tune=20,
        chains=1,
        random_seed=42,
    )
    assert isinstance(result, dict)
    assert "trace" in result
    assert "summary" in result
    assert "tau_posterior" in result
    tau = result["tau_posterior"]
    assert isinstance(tau, np.ndarray)
    assert len(tau) == 50  # draws * chains
    assert tau.dtype.kind in "iu"  # int
    assert result["summary"] is not None
