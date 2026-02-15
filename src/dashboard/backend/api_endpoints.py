# src/dashboard/backend/api_endpoints.py

import os
import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter()

DATA_FOLDER_1 = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/raw"))
DATA_FOLDER_2 = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/processed"))

@router.get("/change_points")
def get_change_points():
    """
    Returns all detected change points as JSON.
    """
    try:
        csv_path = os.path.join(DATA_FOLDER_2, "detected_events.csv")
        print(f"Attempting to read change points from: {csv_path}")
        df = pd.read_csv(csv_path)

        expected_cols = {"Date", "ChangePoint", "MeanBefore", "MeanAfter", "StdDev"}
        if not expected_cols.issubset(df.columns):
            raise HTTPException(status_code=400, detail="CSV missing required columns")

        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        return JSONResponse(content=df.to_dict(orient="records"))

    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        raise HTTPException(status_code=404, detail="Detected events file not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical_prices")
def get_historical_prices():
    """
    Returns historical Brent oil prices for plotting.
    """
    try:
        print(f"The data folder is set to: {DATA_FOLDER_1}")
        csv_path = os.path.join(DATA_FOLDER_1, "BrentOilPrices.csv")
        print(f"Attempting to read historical prices from: {csv_path}")

        df = pd.read_csv(csv_path)

        # Convert Date to datetime with automatic inference
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")  # invalid dates become NaT
        df = df.dropna(subset=["Date"])  # remove rows where Date couldn't be parsed

        # Format to ISO YYYY-MM-DD for frontend
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

        # Ensure Price is numeric
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
        df = df.dropna(subset=["Price"])  # remove rows where Price couldn't be converted

        return JSONResponse(content=df.to_dict(orient="records"))

    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        raise HTTPException(status_code=404, detail="Historical prices file not found")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error reading historical prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))
