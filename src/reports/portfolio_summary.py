import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DB_PATH = "db/nifty100.db"

OUTPUT_DIR = Path("output/portfolio")
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

styles = getSampleStyleSheet()

heading_style = styles["Heading1"]
normal_style = styles["BodyText"]

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_portfolio():

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,

            fr.year,

            fr.return_on_equity_pct,
            fr.roce_pct,
            fr.net_profit_margin_pct,
            fr.operating_profit_margin_pct,
            fr.debt_to_equity,
            fr.composite_quality_score

        FROM companies c

        JOIN sectors s
        ON c.id = s.company_id

        JOIN financial_ratios fr
        ON c.id = fr.company_id

        WHERE fr.year <> 'TTM'

        ORDER BY
            c.id,
            fr.year
        """,
        conn,
    )

    conn.close()

    return df

def trend_arlatest(previous, current):

    if pd.isna(previous) or pd.isna(current):
        return "→"

    if previous == 0:
        return "→"

    pct_change = abs(current - previous) / abs(previous)

    if pct_change <= 0.02:
        return "→"

    if current > previous:
        return "↑"

    return "↓"

def create_portfolio_summary():

    portfolio = load_portfolio()

    groups = portfolio.groupby("id")

    pdf_path = OUTPUT_DIR / "portfolio_summary.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    story = []

    for _, company in groups:

        company = company.sort_values("year")

        latest = company.iloc[-1]

        previous = company.iloc[-2] if len(company) > 1 else latest

        story.append(
            Paragraph(
                f"<b>{latest['company_name']}</b>",
                heading_style,
            )
        )

        story.append(
            Paragraph(
                f"<b>Ticker:</b> {latest['id']}",
                normal_style,
            )
        )

        story.append(
            Paragraph(
                f"<b>Sector:</b> {latest['broad_sector']}",
                normal_style,
            )
        )

        story.append(
            Spacer(
                1,
                0.25 * inch,
            )
        )

        data = [

            ["Metric", "Value"],

            [
                "ROE",
                f"{latest['return_on_equity_pct']:.2f}% {trend_arlatest(previous['return_on_equity_pct'], latest['return_on_equity_pct'])}"
            ],

            [
                "ROCE",
                f"{latest['roce_pct']:.2f}% {trend_arlatest(previous['roce_pct'], latest['roce_pct'])}"
            ],

            [
                "Net Profit Margin",
                f"{latest['net_profit_margin_pct']:.2f}% {trend_arlatest(previous['net_profit_margin_pct'], latest['net_profit_margin_pct'])}"
            ],

            [
                "Operating Margin",
                f"{latest['operating_profit_margin_pct']:.2f}% {trend_arlatest(previous['operating_profit_margin_pct'], latest['operating_profit_margin_pct'])}"
            ],

            [
                "Debt / Equity",
                f"{latest['debt_to_equity']:.2f} {trend_arlatest(previous['debt_to_equity'], latest['debt_to_equity'])}"
            ],

            [
                "Composite Quality Score",
                f"{latest['composite_quality_score']:.2f} {trend_arlatest(previous['composite_quality_score'], latest['composite_quality_score'])}"
            ],

        ]

        table = Table(
            data,
            colWidths=[3 * inch, 2.2 * inch],
        )

        table.setStyle(
            TableStyle([

                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),

                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),

                ("ALIGN", (0,0), (-1,-1), "CENTER"),

                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

                ("BOTTOMPADDING", (0,0), (-1,-1), 8),

                ("TOPPADDING", (0,0), (-1,-1), 8),

            ])
        )

        story.append(table)

        story.append(PageBreak())

    doc.build(story)

    print(f"Generated: {pdf_path}")

if __name__ == "__main__":

        create_portfolio_summary()