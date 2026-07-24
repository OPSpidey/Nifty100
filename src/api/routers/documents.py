import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/companies",
    tags=["Documents"],
)


def get_connection():
    """get_connection function."""
    return sqlite3.connect("db/nifty100.db")


@router.get("/{ticker}/documents")
def documents(ticker: str):
    """documents function."""

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT
            Year,
            Annual_Report
        FROM documents
        WHERE company_id=?
        ORDER BY Year DESC
        """,
        (ticker,),
    ).fetchall()

    conn.close()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    output = []

    for row in rows:

        report = dict(row)

        report["is_url_valid"] = (
            report["Annual_Report"]
            is not None
            and
            report["Annual_Report"].startswith("http")
        )

        output.append(report)

    return output