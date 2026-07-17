import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from reportlab.platypus import Image
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)
import time
import zipfile
from PyPDF2 import PdfReader

DB_PATH = "db/nifty100.db"
OUTPUT_DIR = Path("output/tearsheets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MAX_PROS = 2
MAX_CONS = 3

styles = getSampleStyleSheet()

title_style = styles["Heading1"]
title_style.alignment = TA_CENTER

heading_style = styles["Heading2"]

normal_style = styles["BodyText"]

kpi_style = styles["BodyText"].clone("KPI")

kpi_style.fontName = "Helvetica-Bold"

kpi_style.fontSize = 11

kpi_style.leading = 16

kpi_style.alignment = TA_CENTER

pros_cons_style = styles["BodyText"].clone("ProsCons")

pros_cons_style.fontName = "Helvetica"

pros_cons_style.fontSize = 10

pros_cons_style.leading = 14

pros_cons_style.spaceAfter = 6

table_header_style = styles["BodyText"].clone("TableHeader")

table_header_style.fontName = "Helvetica-Bold"

table_header_style.fontSize = 12

table_header_style.leading = 14

table_header_style.spaceBefore = 0

table_header_style.spaceAfter = 0

table_header_style.alignment = TA_CENTER


def get_connection():
    return sqlite3.connect(DB_PATH)

def load_company(company_id):

    conn = get_connection()

    company = pd.read_sql(
        """
        SELECT *
        FROM companies
        WHERE id=?
        """,
        conn,
        params=[company_id],
    )

    ratios = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    pl = pd.read_sql(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    bs = pd.read_sql(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    cf = pd.read_sql(
        """
        SELECT *
        FROM cashflow
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return company, ratios, pl, bs, cf

def get_all_company_ids():

    conn = get_connection()

    companies = pd.read_sql(
        """
        SELECT id
        FROM companies
        ORDER BY id
        """,
        conn,
    )

    conn.close()

    return companies["id"].tolist()

def fmt(value, suffix=""):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}{suffix}"

def create_kpi_table(ratios):

    latest = (
        ratios[ratios["year"] != "TTM"]
        .sort_values("year")
        .iloc[-1]
    )

    from reportlab.platypus import Paragraph

    data = [
    [
        Paragraph(
            f"<b>ROE</b><br/>{fmt(latest['return_on_equity_pct'], '%')}",
            kpi_style,
        ),
        Paragraph(
            f"<b>ROCE</b><br/>{fmt(latest['roce_pct'], '%')}",
            kpi_style,
        ),
        Paragraph(
            f"<b>Net Profit Margin</b><br/>{fmt(latest['net_profit_margin_pct'], '%')}",
            kpi_style,
        ),
    ],
    [
        Paragraph(
            f"<b>Operating Margin</b><br/>{fmt(latest['operating_profit_margin_pct'], '%')}",
            kpi_style,
        ),
        Paragraph(
            f"<b>Interest Coverage</b><br/>{fmt(latest['interest_coverage'], 'x')}",
            kpi_style,
        ),
        Paragraph(
            f"<b>Debt / Equity</b><br/>{fmt(latest['debt_to_equity'])}",
            kpi_style,
        ),
    ],
]
    
    table = Table(
        data,
        colWidths=[2.0*inch]*3,
        rowHeights=[0.8*inch]*2,
    )

    table.setStyle(TableStyle([

    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),

    ("BACKGROUND", (0,0), (-1,-1), colors.whitesmoke),

    ("ALIGN", (0,0), (-1,-1), "CENTER"),

    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

    ("LEFTPADDING", (0,0), (-1,-1), 8),
    ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),

]))

    return table

def revenue_profit_charts(company_id, pl):

    chart_dir = OUTPUT_DIR / "charts"
    chart_dir.mkdir(parents=True, exist_ok=True)

    latest10 = (
        pl[pl["year"] != "TTM"]
        .tail(10)
        .copy()
    )

    latest10["year"] = latest10["year"].str[-4:]

    revenue_path = chart_dir / f"{company_id}_revenue.png"
    profit_path = chart_dir / f"{company_id}_profit.png"

    # Revenue Chart
    plt.figure(figsize=(4,3))

    plt.bar(
        latest10["year"],
        latest10["sales"],
    )

    plt.title("Revenue")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(revenue_path)

    plt.close()

    # Profit Chart
    plt.figure(figsize=(4,3))

    plt.bar(
        latest10["year"],
        latest10["net_profit"],
    )

    plt.title("Net Profit")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(profit_path)

    plt.close()

    return revenue_path, profit_path

def roe_roce_chart(company_id, ratios):

    chart_dir = OUTPUT_DIR / "charts"
    chart_dir.mkdir(parents=True, exist_ok=True)

    latest10 = (
        ratios[ratios["year"] != "TTM"]
        .tail(10)
        .copy()
    )

    latest10["year"] = latest10["year"].str[-4:]

    output_path = chart_dir / f"{company_id}_roe_roce.png"

    fig, ax1 = plt.subplots(figsize=(6.5, 3))

    ax1.plot(
        latest10["year"],
        latest10["return_on_equity_pct"],
        marker="o",
        label="ROE",
    )

    ax1.set_ylabel("ROE (%)")

    ax2 = ax1.twinx()

    ax2.plot(
        latest10["year"],
        latest10["roce_pct"],
        marker="s",
        label="ROCE",
    )

    ax2.set_ylabel("ROCE (%)")

    plt.title("ROE vs ROCE")

    fig.tight_layout()

    plt.savefig(output_path)

    plt.close()

    return output_path

def balance_sheet_chart(company_id, bs):

    chart_dir = OUTPUT_DIR / "charts"
    chart_dir.mkdir(parents=True, exist_ok=True)

    latest10 = (
        bs.tail(10)
        .copy()
    )

    latest10["equity"] = (
    latest10["equity_capital"]
    + latest10["reserves"]
    )

    latest10["year"] = latest10["year"].str[-4:]

    output_path = chart_dir / f"{company_id}_balance_sheet.png"

    plt.figure(figsize=(6.5, 3.2))

    plt.bar(
        latest10["year"],
        latest10["equity"],
        label="Equity",
    )

    plt.bar(
        latest10["year"],
        latest10["borrowings"],
        bottom=latest10["equity"],
        label="Borrowings",
    )

    plt.bar(
        latest10["year"],
        latest10["other_liabilities"],
        bottom=(
            latest10["equity"]
            + latest10["borrowings"]
        ),
        label="Other Liabilities",
    )

    plt.title("Balance Sheet Composition")

    plt.xticks(rotation=45)

    plt.legend()

    plt.tight_layout()

    plt.savefig(output_path)

    plt.close()

    return output_path

def cashflow_waterfall_chart(company_id, cf):

    if cf.empty:
        return None

    chart_dir = OUTPUT_DIR / "charts"
    chart_dir.mkdir(parents=True, exist_ok=True)

    latest = cf.iloc[-1]

    labels = [
        "CFO",
        "CFI",
        "CFF",
        "Net CF",
    ]

    values = [
        latest["operating_activity"],
        latest["investing_activity"],
        latest["financing_activity"],
        latest["net_cash_flow"],
    ]

    output_path = chart_dir / f"{company_id}_cashflow.png"

    plt.figure(figsize=(6.5, 3))

    bar_colors = [
    "green" if value >= 0 else "red"
    for value in values
    ]

    bars = plt.bar(
    labels,
    values,
    color=bar_colors,
)

    plt.title("Cash Flow Waterfall")

    plt.ylabel("Amount (₹ Cr)")

    plt.axhline(
        0,
        color="black",
        linewidth=1,
    )

    for bar, value in zip(bars, values):

        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()

        if value >= 0:
            offset = (0, 5)
            va = "bottom"
        else:
            offset = (0, -5)
            va = "top"

        plt.annotate(
            f"{value:,.0f}",
            xy=(x, y),
            xytext=offset,
            textcoords="offset points",
            ha="center",
            va=va,
            fontsize=8,
            fontweight="bold",
        )
    ymin, ymax = plt.ylim()

    plt.ylim(
        ymin * 1.15 if ymin < 0 else ymin,
        ymax * 1.15
    )

    plt.tight_layout()
    plt.savefig(output_path)

    plt.close()

    return output_path

def pros_cons_table(company_id):

    df = pd.read_csv("output/pros_cons_generated.csv")

    company = df[df["company_id"] == company_id]

    pros = (
    company[company["type"] == "pro"]["text"]
    .tolist()[:MAX_PROS]
)

    cons = (
        company[company["type"] == "con"]["text"]
        .tolist()[:MAX_CONS]
    )

    if not pros:
        pros = ["No major strengths identified."]

    if not cons:
        cons = ["No major concerns identified."]

    pros_para = [
        Paragraph(
    f'<font color="green">&#9679;</font> {text}',
    pros_cons_style,
)
        for text in pros
    ]

    cons_para = [
        Paragraph(
    f'<font color="red">&#9679;</font> {text}',
    pros_cons_style,
)
        for text in cons
    ]

    table = Table(
        [
            [
                Paragraph("Pros", table_header_style),
                Paragraph("Cons", table_header_style),
            ],
            [
                pros_para,
                cons_para,
            ],
        ],
        colWidths=[3.2*inch, 3.2*inch],
    )

    table.setStyle(TableStyle([

        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),

        ("BACKGROUND", (0,0), (0,0), colors.HexColor("#8BE28B")),

        ("BACKGROUND", (1,0), (1,0), colors.HexColor("#F5B5BF")),

        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

        ("ALIGN", (0,0), (-1,0), "CENTER"),

        ("LEFTPADDING",(0,0),(-1,-1),12),

        ("RIGHTPADDING",(0,0),(-1,-1),12),

        ("TOPPADDING",(0,0),(-1,-1),12),

        ("BOTTOMPADDING",(0,0),(-1,-1),12),

     ]))

    return table

def capital_allocation_badge(label):

    title = Paragraph(
        "<para align='center'><font color='white' size='13'><b>Capital Allocation</b></font></para>",
        normal_style,
    )

    value = Paragraph(
        f"<para align='center'><font color='white' size='24'><b>{label.upper()}</b></font></para>",
        normal_style,
    )

    badge = Table(
        [
            [title],
            [value],
        ],
        colWidths=[6.4 * inch],
        rowHeights=[0.35 * inch, 0.55 * inch],
    )

    badge.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#0B1F3A")),

        ("TEXTCOLOR", (0,0), (-1,-1), colors.white),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),

        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

        ("BOX", (0,0), (-1,-1), 1, colors.black),

        ("TOPPADDING", (0,0), (-1,-1), 8),

        ("BOTTOMPADDING", (0,0), (-1,-1), 8),

    ]))

    badge.hAlign = "CENTER"

    return badge

def create_tearsheet(company_id):

    company, ratios, pl, bs, cf = load_company(company_id)


    if company.empty:
        print(f"{company_id} not found.")
        return

    pdf_path = OUTPUT_DIR / f"{company_id}_tearsheet.pdf"


    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.5 * inch,
    )

    story = []

    company_name = company.iloc[0]["company_name"]
    ticker = company.iloc[0]["id"]

    revenue_chart, profit_chart = revenue_profit_charts(
    company_id,
    pl,
)
    roe_roce = roe_roce_chart(
    company_id,
    ratios,
)
    balance_chart = balance_sheet_chart(
    company_id,
    bs,
)
    cashflow_chart = cashflow_waterfall_chart(
    company_id,
    cf,
)
    allocation = (
    ratios[ratios["year"] != "TTM"]
    .sort_values("year")
    .iloc[-1]["capital_allocation"]
)
    
   

    story.append(
        Spacer(
            1,
            0.10 * inch,
        )
    )

    story.append(
    create_kpi_table(ratios)
)

    story.append(
        Spacer(
            1,
            0.3 * inch,
        )
    )

    chart_table = Table(
    [[
        Image(str(revenue_chart), width=3.2*inch, height=2.4*inch),
        Image(str(profit_chart), width=3.2*inch, height=2.4*inch),
    ]],
    colWidths=[3.2*inch, 3.2*inch],
)

    story.append(chart_table)
    story.append(
    Spacer(
        1,
        0.20 * inch,
    )
)

    story.append(
        Image(
            str(roe_roce),
            width=6.5 * inch,
            height=3 * inch,
        )
    )

    story.append(PageBreak())

    story.append(
    Spacer(
        1,
        0.8 * inch,
    )
)

    story.append(
    Image(
        str(balance_chart),
        width=6.5 * inch,
        height=2.7 * inch,
    )
)

    story.append(
        Spacer(
            1,
            0.25 * inch,
        )
    )

    if cashflow_chart is not None:

        story.append(
            Image(
                str(cashflow_chart),
                width=6.5 * inch,
                height=3 * inch,
            )
        )

    else:

        story.append(
            Paragraph(
                "<b>Cash Flow data not available.</b>",
                heading_style,
            )
        )
    

    story.append(
        Spacer(
            1,
            0.30 * inch,
        )
    )

    story.append(
        pros_cons_table(company_id)
    )

    story.append(
        Spacer(
            1,
            0.20 * inch,
        )
    )

    badge = capital_allocation_badge(allocation)
    badge.hAlign = "CENTER"

    story.append(badge)


    doc.build(
    story,
    onFirstPage=lambda c, d: draw_header(
        c,
        d,
        company_name,
        ticker,
    ),
    onLaterPages=lambda c, d: draw_header(
        c,
        d,
        company_name,
        ticker,
    ),
)

    print(f"Generated: {pdf_path}")

def package_tearsheets():

    pdfs = sorted(
        OUTPUT_DIR.glob("*_tearsheet.pdf")
    )

    if not pdfs:

        print("No tearsheets found.")
        return

    index = []

    for pdf in pdfs:

        index.append(
            {
                "company_id": pdf.stem.replace("_tearsheet", ""),
                "filename": pdf.name,
                "size_kb": round(
                    pdf.stat().st_size / 1024,
                    2,
                ),
            }
        )

    pd.DataFrame(index).to_csv(
        OUTPUT_DIR / "tearsheet_index.csv",
        index=False,
    )

    zip_path = OUTPUT_DIR / "nifty100_tearsheets.zip"

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as zipf:

        for pdf in pdfs:

            zipf.write(
                pdf,
                arcname=pdf.name,
            )

    print("\nPackaging Complete")
    print(f"PDFs : {len(pdfs)}")
    print(f"ZIP  : {zip_path}")

def validate_tearsheets():

    pdfs = sorted(
        OUTPUT_DIR.glob("*_tearsheet.pdf")
    )

    report = []

    for pdf in pdfs:

        try:

            reader = PdfReader(str(pdf))

            report.append(
                {
                    "company_id": pdf.stem.replace("_tearsheet", ""),
                    "pages": len(reader.pages),
                    "status": "PASS",
                }
            )

        except Exception as e:

            report.append(
                {
                    "company_id": pdf.stem.replace("_tearsheet", ""),
                    "pages": 0,
                    "status": f"FAIL: {e}",
                }
            )

    report_df = pd.DataFrame(report)

    report_df.to_csv(
        OUTPUT_DIR / "validation_report.csv",
        index=False,
    )

    passed = (report_df["status"] == "PASS").sum()
    failed = len(report_df) - passed

    print("\nValidation Summary")
    print("===================")
    print(f"Total PDFs : {len(report_df)}")
    print(f"Passed     : {passed}")
    print(f"Failed     : {failed}")

def draw_header(canvas, doc, company_name, ticker): 
    """
    Draw navy header on every page.
    """

    width, height = A4

    canvas.saveState()

    # Navy header
    canvas.setFillColor(colors.HexColor("#0B1F3A"))
    canvas.rect(
        0,
        height - 60,
        width,
        60,
        fill=1,
        stroke=0,
    )

    # Company name
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 20)

    canvas.drawString(
        40,
        height - 38,
        company_name,
    )

    # Ticker
    canvas.setFont("Helvetica", 11)

    ticker_text = f"NSE: {ticker}"

    ticker_width = stringWidth(
        ticker_text,
        "Helvetica",
        11,
    )

    canvas.drawString(
        width - ticker_width - 40,
        height - 38,
        ticker_text,
    )

    canvas.restoreState()


if __name__ == "__main__":

    print("Batch PDF Generation Started")

    start = time.time()

    for pdf in OUTPUT_DIR.glob("*_tearsheet.pdf"):
        pdf.unlink()

    companies = get_all_company_ids()

    success = []
    failed = []
    skipped = []

    for company in companies:

        try:

            conn = get_connection()

            years = pd.read_sql(
                """
                SELECT COUNT(*) AS total
                FROM profitandloss
                WHERE company_id=?
                AND year<>'TTM'
                """,
                conn,
                params=[company],
            ).iloc[0]["total"]

            conn.close()

            if years < 3:

                print(f"Skipping {company} (<3 years data)")

                skipped.append(
                    {
                        "company_id": company,
                        "reason": "Less than 3 years of data",
                    }
                )

                continue

            print(f"Generating {company}...")

            create_tearsheet(company)

            success.append(company)

        except Exception as e:

            print(f"FAILED : {company}")

            print(e)

            failed.append(
                {
                    "company_id": company,
                    "error": str(e),
                }
            )

    if skipped:

        pd.DataFrame(skipped).to_csv(
            "output/skipped_tearsheets.csv",
            index=False,
        )

    elapsed = time.time() - start

    print("\n=================================")
    print("Batch Generation Summary")
    print("=================================")

    print(f"Total Companies : {len(companies)}")
    print(f"Successful      : {len(success)}")
    print(f"Skipped        : {len(skipped)}")
    print(f"Failed         : {len(failed)}")
    print(f"Time Taken      : {elapsed:.2f} sec")

    if failed:

        print("\nSkipped / Failed Companies:")

        for item in failed:
            print(f" - {item['company_id']}")

    print("\nDone.")

    package_tearsheets()

    validate_tearsheets()