import sqlite3
import time
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

START_TIME = time.time()


@router.get("/health")
def health():
    """health function."""
    
    print(DB_PATH)
    print(DB_PATH.exists())

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables = [
        "analysis",
        "balancesheet",
        "cashflow",
        "companies",
        "documents",
        "financial_ratios",
        "market_cap",
        "peer_groups",
        "profitandloss",
        "sectors",
        "stock_prices",
    ]

    db_row_counts = {}

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        db_row_counts[table] = cursor.fetchone()[0]

    conn.close()

    return {
        "status": "ok",
        "db_row_counts": db_row_counts,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": "1.0.0",
    }