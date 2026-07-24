import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


def get_connection():
    """Create database connection."""
    return sqlite3.connect(DB_PATH)


def latest_year_query(alias="c"):
    return f"""
    SELECT year
    FROM financial_ratios f2
    WHERE f2.company_id = {alias}.id
      AND f2.year != 'TTM'
    ORDER BY CAST(SUBSTR(f2.year, -4) AS INTEGER) DESC
    LIMIT 1
    """


@router.get("")
def get_companies(
    sector: str | None = Query(None),
    market_cap_category: str | None = Query(None),
    search: str | None = Query(None),
):
    """Get all companies."""
    conn = get_connection()

    query = """
    SELECT
        c.id,
        c.company_name,
        s.broad_sector,
        s.market_cap_category,
        fr.return_on_equity_pct AS roe_pct,
        fr.roce_pct
    FROM companies c
    LEFT JOIN sectors s
        ON c.id = s.company_id
    LEFT JOIN financial_ratios fr
        ON c.id = fr.company_id
    WHERE fr.year = (
        SELECT year
        FROM financial_ratios f2
        WHERE f2.company_id = c.id
          AND f2.year != 'TTM'
        ORDER BY CAST(SUBSTR(f2.year, -4) AS INTEGER) DESC
        LIMIT 1
    )
    """

    params = []

    if sector:
        query += " AND s.broad_sector = ?"
        params.append(sector)

    if market_cap_category:
        query += " AND s.market_cap_category = ?"
        params.append(market_cap_category)

    if search:
        query += """
        AND (
            c.id LIKE ?
            OR c.company_name LIKE ?
        )
        """
        value = f"%{search}%"
        params.extend([value, value])

    query += " ORDER BY c.company_name"

    rows = conn.execute(query, params).fetchall()

    columns = [
        "id",
        "company_name",
        "broad_sector",
        "market_cap_category",
        "roe_pct",
        "roce_pct",
    ]

    conn.close()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


@router.get("/{ticker}")
def get_company(ticker: str):
    """Get company details."""
    conn = get_connection()

    query = """
    SELECT
        c.*,
        s.*,
        fr.*
    FROM companies c
    LEFT JOIN sectors s
        ON c.id = s.company_id
    LEFT JOIN financial_ratios fr
        ON c.id = fr.company_id
    WHERE c.id = ?
      AND fr.year = (
        SELECT year
        FROM financial_ratios f2
        WHERE f2.company_id = c.id
          AND f2.year != 'TTM'
        ORDER BY CAST(SUBSTR(f2.year, -4) AS INTEGER) DESC
        LIMIT 1
      )
    """

    cursor = conn.execute(
        query,
        (ticker.upper(),)
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    columns = [
        col[0]
        for col in cursor.description
    ]

    result = dict(zip(columns, row))

    conn.close()

    return result


@router.get("/{ticker}/pl")
def get_profit_and_loss(
    ticker: str,
    from_year: str | None = Query(None),
    to_year: str | None = Query(None),
):
    """Get profit and loss data."""
    return get_table_data(
        "profitandloss",
        ticker,
        from_year,
        to_year,
    )


@router.get("/{ticker}/bs")
def get_balance_sheet(
    ticker: str,
    from_year: str | None = Query(None),
    to_year: str | None = Query(None),
):
    """Get balance sheet data."""
    return get_table_data(
        "balancesheet",
        ticker,
        from_year,
        to_year,
    )


@router.get("/{ticker}/cashflow")
def get_cashflow(
    ticker: str,
    from_year: str | None = Query(None),
    to_year: str | None = Query(None),
):
    """Get cashflow data."""
    return get_table_data(
        "cashflow",
        ticker,
        from_year,
        to_year,
    )


def get_table_data(
    table,
    ticker,
    from_year=None,
    to_year=None,
):
    """Get financial table data."""
    conn = get_connection()

    query = f"""
    SELECT *
    FROM {table}
    WHERE company_id = ?
    """

    params = [ticker.upper()]

    if from_year:
        query += " AND year >= ?"
        params.append(from_year)

    if to_year:
        query += " AND year <= ?"
        params.append(to_year)

    query += " ORDER BY year"

    cursor = conn.execute(query, params)

    rows = cursor.fetchall()

    if not rows:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Data not found",
        )

    columns = [
        col[0]
        for col in cursor.description
    ]

    conn.close()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


@router.get("/{ticker}/ratios")
def get_ratios(
    ticker: str,
    year: str | None = Query(None),
):
    """Get company ratios."""
    conn = get_connection()

    query = """
    SELECT *
    FROM financial_ratios
    WHERE company_id = ?
    """

    params = [ticker.upper()]

    if year:
        query += " AND year = ?"
        params.append(year)

    rows = conn.execute(query, params).fetchall()

    columns = [
        col[0]
        for col in conn.execute(query, params).description
    ]

    conn.close()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


@router.get("/{ticker}/tearsheet")
def get_tearsheet(ticker: str):
    """Get PDF tearsheet."""

    pdf_path = (
        PROJECT_ROOT
        / "reports"
        / "tearsheets"
        / f"{ticker.upper()}.pdf"
    )

    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Tearsheet not found",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )