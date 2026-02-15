# src/dashboard/backend/app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from .api_endpoints import router as api_router
except ImportError:
    from api_endpoints import router as api_router

app = FastAPI(title="Brent Oil Change Point API")

# Allow React frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
