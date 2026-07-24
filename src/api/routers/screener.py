import sqlite3

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/screener", tags=["Screener"])


def get_connection():
    """get_connection function."""
    return sqlite3.connect("db/nifty100.db")


@router.get("")
def screener(
    min_roe: float | None = Query(None),
    max_de: float | None = Query(None),
    min_fcf: float | None = Query(None),
    sector: str | None = Query(None),
    min_rev_cagr_5yr: float | None = Query(None),
    min_pat_cagr_5yr: float | None = Query(None),
    max_pe: float | None = Query(None),
):
    """screener function."""

    if min_roe is not None and min_roe < 0:
        raise HTTPException(status_code=400, detail="Invalid min_roe")

    if max_de is not None and max_de < 0:
        raise HTTPException(status_code=400, detail="Invalid max_de")

    if min_fcf is not None and min_fcf < 0:
        raise HTTPException(status_code=400, detail="Invalid min_fcf")

    if min_rev_cagr_5yr is not None and min_rev_cagr_5yr < -100:
        raise HTTPException(status_code=400, detail="Invalid revenue CAGR")

    if min_pat_cagr_5yr is not None and min_pat_cagr_5yr < -100:
        raise HTTPException(status_code=400, detail="Invalid PAT CAGR")

    if max_pe is not None and max_pe <= 0:
        raise HTTPException(status_code=400, detail="Invalid max_pe")

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    query = """
    SELECT
        c.id,
        c.company_name,
        s.broad_sector,
        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.free_cash_flow_cr,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        mc.pe_ratio
    FROM companies c
    JOIN sectors s
        ON c.id = s.company_id
    JOIN financial_ratios fr
        ON c.id = fr.company_id
    JOIN market_cap mc
        ON c.id = mc.company_id
       AND mc.year = 2024
    WHERE fr.year = (
        SELECT MAX(year)
        FROM financial_ratios f2
        WHERE f2.company_id = c.id
    )
    """

    params = []

    if min_roe is not None:
        query += " AND fr.return_on_equity_pct >= ?"
        params.append(min_roe)

    if max_de is not None:
        query += " AND fr.debt_to_equity <= ?"
        params.append(max_de)

    if min_fcf is not None:
        query += " AND fr.free_cash_flow_cr >= ?"
        params.append(min_fcf)

    if sector:
        query += " AND s.broad_sector = ?"
        params.append(sector)

    if min_rev_cagr_5yr is not None:
        query += " AND fr.revenue_cagr_5yr >= ?"
        params.append(min_rev_cagr_5yr)

    if min_pat_cagr_5yr is not None:
        query += " AND fr.pat_cagr_5yr >= ?"
        params.append(min_pat_cagr_5yr)

    if max_pe is not None:
        query += " AND mc.pe_ratio <= ?"
        params.append(max_pe)

    query += """
    ORDER BY
        fr.return_on_equity_pct DESC,
        fr.revenue_cagr_5yr DESC
    """

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [dict(row) for row in rows]