import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DB_PATH = "db/nifty100.db"

OUTPUT_DIR = Path("output/sector_reports")
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


styles = getSampleStyleSheet()

heading_style = styles["Heading1"]
normal_style = styles["BodyText"]

def get_connection():

    return sqlite3.connect(DB_PATH)



def load_sector_data(sector):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector,
            fr.return_on_equity_pct,
            fr.roce_pct,
            fr.net_profit_margin_pct,
            fr.operating_profit_margin_pct,
            fr.debt_to_equity,
            fr.interest_coverage,
            fr.asset_turnover,
            fr.composite_quality_score

        FROM companies c

        JOIN sectors s
        ON c.id = s.company_id

        JOIN financial_ratios fr
        ON c.id = fr.company_id

        WHERE s.broad_sector = ?

        AND fr.year = (
            SELECT MAX(year)
            FROM financial_ratios
            WHERE company_id = c.id
            AND year <> 'TTM'
        )

        """,
        conn,
        params=[sector],
    )

    conn.close()

    return df

def create_sector_report(sector):

    df = load_sector_data(sector)

    if df.empty:

        return


    filename = (
        sector
        .replace(" ","_")
        + "_report.pdf"
    )


    path = OUTPUT_DIR / filename


    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )


    story=[]


    story.append(
        Paragraph(
            f"{sector} Sector Report",
            heading_style,
        )
    )

    story.append(
        Spacer(1,20)
    )


    median = df.median(
        numeric_only=True
    )


    summary = [
        ["Metric","Median Value"],

        [
            "ROE",
            f"{median['return_on_equity_pct']:.2f}%"
        ],

        [
            "ROCE",
            f"{median['roce_pct']:.2f}%"
        ],

        [
            "Net Margin",
            f"{median['net_profit_margin_pct']:.2f}%"
        ],

        [
            "OPM",
            f"{median['operating_profit_margin_pct']:.2f}%"
        ],

    ]


    table = Table(summary)

    table.setStyle(
        TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ])
    )


    story.append(table)

    story.append(
        Spacer(1,20)
    )


    data = [
        [
            "Company",
            "ROE",
            "ROCE",
            "NPM",
            "OPM",
            "D/E",
            "ICR",
            "Score",
        ]
    ]


    for _,row in df.iterrows():

        data.append(
            [
                row["company_name"],
                round(row["return_on_equity_pct"],2),
                round(row["roce_pct"],2),
                round(row["net_profit_margin_pct"],2),
                round(row["operating_profit_margin_pct"],2),
                round(row["debt_to_equity"],2),
                round(row["interest_coverage"],2),
                round(row["composite_quality_score"],2),
            ]
        )


    company_table = Table(
        data,
        repeatRows=1,
    )


    company_table.setStyle(
        TableStyle([
            ("GRID",(0,0),(-1,-1),0.25,colors.grey),
            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
        ])
    )


    story.append(company_table)


    doc.build(story)


    print(
        f"Generated: {path}"
    )

if __name__ == "__main__":

    conn = get_connection()

    sectors = pd.read_sql(
        """
        SELECT DISTINCT broad_sector
        FROM sectors
        ORDER BY broad_sector
        """,
        conn,
    )["broad_sector"].tolist()

    conn.close()


    print(
        f"Generating {len(sectors)} sector reports"
    )


    for sector in sectors:

        create_sector_report(sector)


    print("Done.")