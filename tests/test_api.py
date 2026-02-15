# tests/test_api.py
"""
Pytest suite for the dashboard API (src.dashboard.backend).
Uses FastAPI TestClient and patches data paths to fixture CSVs.
"""

import pytest
from unittest.mock import patch
from pathlib import Path

from fastapi.testclient import TestClient
from src.dashboard.backend.app import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures: temporary data folders and CSVs
# ---------------------------------------------------------------------------

@pytest.fixture
def raw_folder(tmp_path):
    """Temporary folder with a valid BrentOilPrices.csv."""
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "BrentOilPrices.csv").write_text(
        "Date,Price\n"
        "2020-01-01,65.50\n"
        "2020-01-02,66.00\n"
        "2020-01-03,65.25\n"
    )
    return raw


@pytest.fixture
def processed_folder(tmp_path):
    """Temporary folder with valid detected_events.csv (required columns)."""
    processed = tmp_path / "processed"
    processed.mkdir()
    (processed / "detected_events.csv").write_text(
        "Date,ChangePoint,MeanBefore,MeanAfter,StdDev\n"
        "2020-06-15,1,0.01,0.02,0.01\n"
        "2021-03-10,2,-0.005,0.008,0.012\n"
    )
    return processed


@pytest.fixture
def mock_both_folders(raw_folder, processed_folder):
    """Patch API to use tmp raw and processed folders."""
    with patch("src.dashboard.backend.api_endpoints.DATA_FOLDER_1", str(raw_folder)):
        with patch("src.dashboard.backend.api_endpoints.DATA_FOLDER_2", str(processed_folder)):
            yield


# ---------------------------------------------------------------------------
# GET /api/historical_prices
# ---------------------------------------------------------------------------

def test_historical_prices_returns_200_and_list(mock_both_folders):
    """GET /api/historical_prices returns 200 and a JSON list."""
    response = client.get("/api/historical_prices")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3


def test_historical_prices_records_have_date_and_price(mock_both_folders):
    """Each record has Date and Price keys with expected types/format."""
    response = client.get("/api/historical_prices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    for row in data:
        assert "Date" in row
        assert "Price" in row
        assert row["Date"] == "2020-01-01" or row["Date"] == "2020-01-02" or row["Date"] == "2020-01-03"
    assert data[0]["Date"] == "2020-01-01"
    assert data[0]["Price"] == 65.5


def test_historical_prices_404_when_file_missing(tmp_path):
    """GET /api/historical_prices returns 404 when BrentOilPrices.csv is absent."""
    raw = tmp_path / "raw"
    raw.mkdir()
    # No CSV file
    with patch("src.dashboard.backend.api_endpoints.DATA_FOLDER_1", str(raw)):
        response = client.get("/api/historical_prices")
    assert response.status_code == 404
    detail = response.json().get("detail", "")
    assert "not found" in detail.lower() or "historical" in detail.lower() or "file" in detail.lower()


def test_historical_prices_drops_invalid_dates(raw_folder, processed_folder):
    """Rows with unparseable dates are dropped; valid rows returned."""
    (raw_folder / "BrentOilPrices.csv").write_text(
        "Date,Price\n"
        "2020-01-01,65.0\n"
        "not-a-date,66.0\n"
        "2020-01-03,67.0\n"
    )
    with patch("src.dashboard.backend.api_endpoints.DATA_FOLDER_1", str(raw_folder)):
        with patch("src.dashboard.backend.api_endpoints.DATA_FOLDER_2", str(processed_folder)):
            response = client.get("/api/historical_prices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    dates = [r["Date"] for r in data]
    assert "2020-01-01" in dates
    assert "2020-01-03" in dates


# ---------------------------------------------------------------------------
# GET /api/change_points
# ---------------------------------------------------------------------------

def test_change_points_returns_200_and_list(mock_both_folders):
    """GET /api/change_points returns 200 and a JSON list."""
    response = client.get("/api/change_points")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_change_points_records_have_required_fields(mock_both_folders):
    """Each record has Date, ChangePoint, MeanBefore, MeanAfter, StdDev."""
    response = client.get("/api/change_points")
    assert response.status_code == 200
    data = response.json()
    required = {"Date", "ChangePoint", "MeanBefore", "MeanAfter", "StdDev"}
    for row in data:
        assert required.issubset(row.keys()), f"Missing keys in {row}"
    assert data[0]["Date"] == "2020-06-15"
    assert data[0]["MeanBefore"] == 0.01
    assert data[0]["MeanAfter"] == 0.02


def test_change_points_404_when_file_missing(raw_folder, tmp_path):
    """GET /api/change_points returns 404 when detected_events.csv is absent."""
    processed = tmp_path / "processed"
    processed.mkdir()
    # No detected_events.csv
    with patch("src.dashboard.backend.api_endpoints.DATA_FOLDER_1", str(raw_folder)):
        with patch("src.dashboard.backend.api_endpoints.DATA_FOLDER_2", str(processed)):
            response = client.get("/api/change_points")
    assert response.status_code == 404
    detail = response.json().get("detail", "")
    assert "not found" in detail.lower() or "events" in detail.lower() or "file" in detail.lower()


def test_change_points_400_when_columns_missing(raw_folder, processed_folder):
    """GET /api/change_points returns 400 when CSV lacks required columns."""
    (processed_folder / "detected_events.csv").write_text(
        "Date,MeanBefore,MeanAfter\n"
        "2020-06-15,0.01,0.02\n"
    )
    with patch("src.dashboard.backend.api_endpoints.DATA_FOLDER_1", str(raw_folder)):
        with patch("src.dashboard.backend.api_endpoints.DATA_FOLDER_2", str(processed_folder)):
            response = client.get("/api/change_points")
    assert response.status_code == 400
    assert "column" in response.json().get("detail", "").lower() or "required" in response.json().get("detail", "").lower()


# ---------------------------------------------------------------------------
# General API
# ---------------------------------------------------------------------------

def test_api_prefix(mock_both_folders):
    """Routes under /api return JSON; historical_prices and change_points are reachable."""
    r1 = client.get("/api/historical_prices")
    r2 = client.get("/api/change_points")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert isinstance(r1.json(), list)
    assert isinstance(r2.json(), list)
