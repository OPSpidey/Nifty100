# Nifty100 Financial Analytics Platform

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.140-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.60-red)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue)
![Pytest](https://img.shields.io/badge/Tests-201%20Passed-success)
![Ruff](https://img.shields.io/badge/Ruff-Clean-success)

## Overview

Nifty100 Analytics Platform is an end-to-end financial analytics system that analyzes Nifty100 companies using financial statements, valuation metrics, cash flow analysis, peer comparison, and stock screening.

The platform integrates an ETL pipeline, SQLite database, analytics engine, FastAPI REST API, and Streamlit dashboard to provide interactive financial insights.

---

## Features

- Financial data ETL pipeline
- SQLite data warehouse
- 20+ financial KPIs and ratio engine
- Revenue, PAT, and EPS CAGR analysis
- Composite Quality Score
- Cash Flow & Capital Allocation analysis
- Multi-factor Stock Screener
- Peer & Sector Analysis
- Company Valuation
- FastAPI REST API
- Interactive Streamlit Dashboard
- Automated Reports
- 201 Automated Tests

---

## Tech Stack

| Category | Technologies |
|-----------|--------------|
| Language | Python |
| Backend | FastAPI |
| Dashboard | Streamlit |
| Database | SQLite |
| Analytics | Pandas, NumPy |
| Visualization | Plotly, Matplotlib |
| Machine Learning | Scikit-learn |
| Testing | Pytest |
| Code Quality | Ruff, Black |

---

## Project Structure

```text
Nifty100/
├── data/
├── db/
├── docs/
├── output/
├── reports/
├── scripts/
├── src/
│   ├── analytics/
│   ├── api/
│   ├── dashboard/
│   ├── dq/
│   ├── etl/
│   ├── nlp/
│   ├── ratios/
│   ├── reports/
│   └── screener/
├── tests/
├── requirements.txt
└── README.md
```

---

## Dashboard Modules

- Home
- Company Profile
- Stock Screener
- Peer Analysis
- Trend Analysis
- Sector Analysis
- Capital Allocation
- Reports

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/v1/health` | Health Check |
| `/api/v1/companies` | Company Information |
| `/api/v1/screener` | Stock Screener |
| `/api/v1/sectors` | Sector Analysis |
| `/api/v1/peers` | Peer Comparison |
| `/api/v1/valuation` | Company Valuation |
| `/api/v1/portfolio` | Portfolio Analytics |
| `/api/v1/documents` | Company Documents |

---

## Installation

```bash
git clone <repository-url>
cd Nifty100

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

python -m pip install -r requirements.txt
```

---

## Run the Application

### FastAPI

```bash
uvicorn src.api.main:app --reload
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

### Streamlit Dashboard

```bash
streamlit run src/dashboard/app.py
```

Dashboard:

```
http://localhost:8501
```

---

## Testing

Run all tests

```bash
python -m pytest
```

Run Ruff

```bash
python -m ruff check .
```

Compile Project

```bash
python -m compileall src tests
```

---

## Outputs

The platform generates:

- Financial Ratio Database
- Stock Screener Reports
- Peer Comparison Reports
- Capital Allocation Reports
- Valuation Reports
- Company PDF Tearsheets
- Validation Reports

---

## Future Improvements

- Docker Support
- CI/CD Pipeline
- Cloud Deployment
- User Authentication
- Real-time Market Data Integration

---
