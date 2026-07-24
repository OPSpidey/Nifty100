from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet


OUTPUT = "docs/analyst_guide.pdf"


doc = SimpleDocTemplate(
    OUTPUT,
    title="Nifty100 Analytics Platform - Analyst Guide"
)


styles = getSampleStyleSheet()

story = []


def add_page(title, content):

    story.append(
        Paragraph(title, styles["Heading1"])
    )

    story.append(
        Spacer(1, 12)
    )

    story.append(
        Paragraph(content, styles["BodyText"])
    )

    story.append(PageBreak())


pages = [

(
"1. Project Introduction",
"""
The Nifty100 Analytics Platform is a financial analytics system
designed to analyze Nifty100 companies using fundamental,
valuation, profitability, cashflow and peer comparison metrics.

The platform combines ETL pipelines, SQLite storage, FastAPI
services and a Streamlit dashboard to provide analyst-friendly
insights.
"""
),

(
"2. System Overview",
"""
The system contains four major layers:

1. ETL Layer:
Loads and cleans financial datasets.

2. Analytics Engine:
Calculates financial ratios including ROE, ROCE, margins,
cashflow metrics and CAGR.

3. API Layer:
Provides company, screener, sector and peer endpoints.

4. Dashboard Layer:
Provides interactive visual analysis.
"""
),

(
"3. Streamlit Dashboard Navigation",
"""
The Streamlit dashboard contains multiple screens:

Home:
Provides overall platform overview.

Company Profile:
Displays company fundamentals, ratios and financial information.

Screener:
Allows filtering companies using financial conditions.

Peers:
Provides peer comparison analysis.

Trends:
Shows historical financial trends.

Sectors:
Provides sector-level analysis.

Capital:
Displays capital allocation insights.

Reports:
Generates analyst reports and PDF tearsheets.
"""
),

(
"4. Using the Screener",
"""
The screener helps analysts identify companies based on
financial quality parameters.

Available filters include:

- Minimum ROE
- Maximum Debt-to-Equity
- Minimum Free Cash Flow
- Sector filtering
- Revenue CAGR
- PAT CAGR
- Maximum PE ratio

Apply filters and review the ranked company results.
"""
),

(
"5. Company Profile Analysis",
"""
The Company Profile page provides:

- Company information
- Profitability ratios
- ROE and ROCE
- Debt metrics
- Cashflow metrics
- Growth indicators
- Historical financial information

Select a ticker to view detailed analysis.
"""
),

(
"6. Sector and Peer Analysis",
"""
Sector Analysis provides:

- Sector company count
- Median valuation metrics
- Sector comparisons

Peer Analysis compares companies within similar
business groups using financial KPIs.
"""
),

(
"7. Generating PDF TearSheets",
"""
Analysts can generate PDF tearsheets from the Reports section.

A tearsheet contains:

- Company overview
- Financial ratios
- Growth metrics
- Valuation information
- Analyst insights

Use the report option from the dashboard to create PDFs.
"""
),

(
"8. API Usage Guide",
"""
The FastAPI service provides programmatic access.

Base URL:

http://127.0.0.1:8000

Important endpoints:

/api/v1/health

/api/v1/companies

/api/v1/screener

/api/v1/sectors

/api/v1/peers
"""
),

(
"9. API Curl Examples",
"""
Health Check:

curl http://127.0.0.1:8000/api/v1/health


Company Data:

curl http://127.0.0.1:8000/api/v1/companies/TCS


Screener:

curl "http://127.0.0.1:8000/api/v1/screener?min_roe=15"
"""
),

(
"10. Troubleshooting Guide",
"""
Common issues:

API not starting:
Check if port 8000 is already occupied.

Dashboard not loading:
Ensure Streamlit is running on port 8501.

Database errors:
Verify db/nifty100.db exists.

Missing packages:
Activate the virtual environment and install
requirements.

For API issues check /docs Swagger documentation.
"""
),

]


for title, content in pages:
    add_page(title, content)


doc.build(story)

print("Analyst guide created:", OUTPUT)