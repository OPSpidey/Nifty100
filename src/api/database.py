import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


def get_connection():
    """Create and return a SQLite connection."""
    return sqlite3.connect(DB_PATH)