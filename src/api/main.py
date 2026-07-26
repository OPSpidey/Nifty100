import time

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

START_TIME = time.time()

app = FastAPI(
    title="Nifty100 Analytics API",
    description="Financial Analytics API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):

    response = await call_next(request)

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