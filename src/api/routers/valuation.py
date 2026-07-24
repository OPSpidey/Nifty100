import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/market-cap",
    tags=["Market Cap"],
)


def get_connection():
    """get_connection function."""
    return sqlite3.connect("db/nifty100.db")


@router.get("/{ticker}")
def market_cap_history(ticker: str):
    """market_cap_history function."""

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT
            year,
            market_cap_crore,
            enterprise_value_crore,
            pe_ratio,
            pb_ratio,
            ev_ebitda,
            dividend_yield_pct
        FROM market_cap
        WHERE
            company_id=?
            AND year BETWEEN 2019 AND 2024
        ORDER BY year
        """,
        (ticker,),
    ).fetchall()

    conn.close()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    return [dict(row) for row in rows]