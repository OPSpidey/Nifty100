import sqlite3
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import (
    companies,
    documents,
    health,
    peers,
    portfolio,
    screener,
    sectors,
    valuation,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

START_TIME = time.time()

app = FastAPI(
    title="Nifty100 Analytics API",
    description="Financial Analytics API",
    version="1.0.0",
)

def get_connection():
    """get_connection function."""
    return sqlite3.connect(DB_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):

    start = time.perf_counter()

    response = await call_next(request)

    elapsed = time.perf_counter() - start

    print(
        f"{request.method} "
        f"{request.url.path} "
        f"{elapsed:.4f}s"
    )

    return response

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)

app.include_router(
    companies.router,
    prefix="/api/v1",
    tags=["Companies"],
)

app.include_router(
    screener.router,
    prefix="/api/v1",
    tags=["Screener"],
)

app.include_router(
    sectors.router,
    prefix="/api/v1",
    tags=["Sectors"],
)

app.include_router(
    peers.router,
    prefix="/api/v1",
    tags=["Peers"],
)

app.include_router(
    valuation.router,
    prefix="/api/v1",
    tags=["Valuation"],
)

app.include_router(
    portfolio.router,
    prefix="/api/v1",
    tags=["Portfolio"],
)

app.include_router(
    documents.router,
    prefix="/api/v1",
    tags=["Documents"],
)