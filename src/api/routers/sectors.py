import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/sectors",
    tags=["Sectors"],
)


def get_connection():
    """get_connection function."""
    return sqlite3.connect("db/nifty100.db")


@router.get("")
def get_sectors():
    """get_sectors function."""

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT
            s.broad_sector,
            COUNT(DISTINCT s.company_id) AS company_count,
            ROUND(AVG(fr.return_on_equity_pct),2) AS median_roe,
            ROUND(AVG(mc.pe_ratio),2) AS median_pe,
            ROUND(AVG(fr.debt_to_equity),2) AS median_de
        FROM sectors s
        JOIN financial_ratios fr
            ON s.company_id = fr.company_id
        LEFT JOIN market_cap mc
            ON s.company_id = mc.company_id
            AND mc.year = 2024
        WHERE fr.year = (
            SELECT MAX(f2.year)
            FROM financial_ratios f2
            WHERE f2.company_id = fr.company_id
        )
        GROUP BY s.broad_sector
        ORDER BY s.broad_sector
        """
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


@router.get("/{sector}/companies")
def sector_companies(sector: str):
    """sector_companies function."""

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    exists = conn.execute(
        """
        SELECT 1
        FROM sectors
        WHERE broad_sector = ?
        LIMIT 1
        """,
        (sector,),
    ).fetchone()

    if exists is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Unknown sector",
        )

    rows = conn.execute(
        """
        SELECT
            c.id,
            c.company_name,
            fr.return_on_equity_pct,
            fr.roce_pct,
            fr.debt_to_equity,
            fr.net_profit_margin_pct,
            fr.operating_profit_margin_pct,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            fr.free_cash_flow_cr
        FROM companies c
        JOIN sectors s
            ON c.id = s.company_id
        JOIN financial_ratios fr
            ON c.id = fr.company_id
        WHERE
            s.broad_sector = ?
            AND fr.year = (
                SELECT MAX(f2.year)
                FROM financial_ratios f2
                WHERE f2.company_id = c.id
            )
        ORDER BY c.company_name
        """,
        (sector,),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]