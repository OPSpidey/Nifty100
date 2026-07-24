import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/peers",
    tags=["Peers"],
)


def get_connection():
    """get_connection function."""
    return sqlite3.connect("db/nifty100.db")


METRICS = [
    "return_on_equity_pct",
    "roce_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "free_cash_flow_cr",
    "asset_turnover",
    "interest_coverage",
]


@router.get("/{group_name}")
def peer_group(group_name: str):
    """peer_group function."""

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    exists = conn.execute(
        """
        SELECT 1
        FROM peer_groups
        WHERE peer_group_name=?
        LIMIT 1
        """,
        (group_name,),
    ).fetchone()

    if exists is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Unknown peer group",
        )

    query = f"""
    SELECT
        pg.company_id,
        c.company_name,
        {",".join("fr."+m for m in METRICS)}
    FROM peer_groups pg
    JOIN companies c
        ON pg.company_id=c.id
    JOIN financial_ratios fr
        ON pg.company_id=fr.company_id
    WHERE
        pg.peer_group_name=?
        AND fr.year=(
            SELECT MAX(f2.year)
            FROM financial_ratios f2
            WHERE f2.company_id=pg.company_id
        )
    ORDER BY c.company_name
    """

    rows = conn.execute(query, (group_name,)).fetchall()

    import pandas as pd

    df = pd.DataFrame(rows, columns=rows[0].keys())

    for metric in METRICS:
        df[f"{metric}_percentile"] = (
            df[metric]
            .rank(pct=True)
            .mul(100)
            .round(2)
        )

    conn.close()

    return df.to_dict(orient="records")

@router.get("/compare/{ticker}")
def compare_peer(ticker: str):
    """compare_peer function."""

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    peer = conn.execute(
        """
        SELECT peer_group_name
        FROM peer_groups
        WHERE company_id=?
        """,
        (ticker,),
    ).fetchone()

    if peer is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    peer_group = peer["peer_group_name"]

    benchmark = conn.execute(
        """
        SELECT company_id
        FROM peer_groups
        WHERE
            peer_group_name=?
            AND is_benchmark=1
        """,
        (peer_group,),
    ).fetchone()

    metrics = [
        "return_on_equity_pct",
        "roce_pct",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "asset_turnover",
    ]

    def latest(company):
        """latest function."""

        sql = f"""
        SELECT
        {",".join(metrics)}
        FROM financial_ratios
        WHERE
            company_id=?
            AND year=(
                SELECT MAX(year)
                FROM financial_ratios
                WHERE company_id=?
            )
        """

        row = conn.execute(
            sql,
            (company, company),
        ).fetchone()

        return dict(row)

    company_values = latest(ticker)

    benchmark_values = latest(
        benchmark["company_id"]
    )

    avg_sql = f"""
    SELECT
    {",".join(f"AVG({m}) AS {m}" for m in metrics)}
    FROM financial_ratios fr
    JOIN peer_groups pg
        ON fr.company_id=pg.company_id
    WHERE
        pg.peer_group_name=?
        AND fr.year=(
            SELECT MAX(f2.year)
            FROM financial_ratios f2
            WHERE f2.company_id=fr.company_id
        )
    """

    peer_average = dict(
        conn.execute(
            avg_sql,
            (peer_group,),
        ).fetchone()
    )

    conn.close()

    return {
        "peer_group": peer_group,
        "company": company_values,
        "peer_average": peer_average,
        "benchmark": benchmark_values,
    }