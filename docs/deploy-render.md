# Deploy on Render

This project can be deployed on [Render](https://render.com) as two services: a **Python backend** (FastAPI) and a **static frontend** (React + Vite). The repo includes a `render.yaml` Blueprint so you can deploy both from the dashboard.

## Prerequisites

- A [Render](https://render.com) account (free tier is fine).
- This repo pushed to **GitHub** (or GitLab) and connected to Render.

## 1. Deploy with Blueprint (recommended)

1. Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**.
2. Connect the repository that contains this project (e.g. `Deregit2025/oil-price-changepoint-analysis-ml-dashboard`).
3. Render will detect `render.yaml` and show two services:
   - **brent-oil-api** (backend)
   - **brent-oil-dashboard** (frontend)
4. Click **Apply** to create both services. Render will build and deploy them.
5. After the **backend** finishes deploying, copy its URL (e.g. `https://brent-oil-api.onrender.com`).
6. In the **frontend** service → **Environment** → add (or edit):
   - **Key:** `VITE_API_URL`  
   - **Value:** your backend URL, e.g. `https://brent-oil-api.onrender.com`  
   (no trailing slash)
7. Trigger a **manual deploy** of the frontend so the new env var is used in the build.

After that, open the frontend URL (e.g. `https://brent-oil-dashboard.onrender.com`). The app will call the backend for prices and change points.

## 2. Data files on the backend

The API reads from:

- `data/raw/BrentOilPrices.csv` (historical prices)
- `data/processed/detected_events.csv` (change points)

These paths are relative to the repo root. As long as these files are committed in the repo, the backend on Render will find them. If they are missing, the API will return 404 for those endpoints; add the CSVs and redeploy if needed.

## 3. Manual setup (without Blueprint)

If you prefer to create the services by hand:

### Backend (Web Service)

- **Runtime:** Python 3
- **Build command:** `pip install -r requirements-ci.txt`
- **Start command:** `uvicorn src.dashboard.backend.app:app --host 0.0.0.0 --port $PORT`
- **Root directory:** leave empty (repo root).

Render sets `PORT` automatically; the app uses it.

### Frontend (Static Site)

- **Build command:** `cd src/dashboard/frontend && npm install && npm run build`
- **Publish directory:** `src/dashboard/frontend/dist`
- **Environment variable:** `VITE_API_URL` = your backend URL (e.g. `https://brent-oil-api.onrender.com`).

Redeploy the frontend after setting `VITE_API_URL`.

## 4. Free tier notes

- Backend free services spin down after inactivity; the first request after idle may be slow (cold start).
- Frontend static sites are always on and typically fast.

## 5. Troubleshooting

- **Frontend shows “network error” or no data:**  
  Ensure `VITE_API_URL` is set to the backend URL (no trailing slash) and redeploy the frontend.

- **Backend 404 for `/api/historical_prices` or `/api/change_points`:**  
  Check that `data/raw/BrentOilPrices.csv` and `data/processed/detected_events.csv` exist in the repo and that the backend is using the repo root as its working directory.

- **Backend build fails (e.g. pywinpty):**  
  The Blueprint uses `requirements-ci.txt`, which omits Windows-only packages. If you switch to `requirements.txt`, consider keeping a CI/production requirements file without `pywinpty` for Render.
