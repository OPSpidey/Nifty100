# Nifty100 Analytics Platform

## Overview

Nifty100 Analytics Platform is an end-to-end financial analytics system for analyzing Nifty100 companies using fundamental analysis, financial ratios, valuation metrics, cash flow analysis, peer comparison, and stock screening.

The platform integrates an ETL pipeline, SQLite data warehouse, analytics engine, FastAPI REST API, and Streamlit dashboard to provide investment insights through interactive visualizations and automated financial analysis.

---

## Key Features

- Automated ETL pipeline for financial data ingestion and validation
- Financial ratio engine with 20+ key performance indicators
- Profitability, leverage, liquidity, efficiency, and cash flow analysis
- Revenue, PAT, and EPS CAGR calculations
- Composite Quality Score generation
- Capital allocation pattern analysis
- Multi-factor stock screener with predefined investment filters
- Peer comparison and sector benchmarking
- Company valuation analysis
- Interactive Streamlit dashboard
- FastAPI REST API
- PDF company tearsheet generation
- Data quality validation and automated testing

---

## Technology Stack

### Programming Language

- Python

### Backend

- FastAPI
- SQLite

### Analytics

- Pandas
- NumPy

### Visualization

- Streamlit
- Plotly

### Testing & Code Quality

- Pytest
- Ruff
- Black

---

## Project Architecture

```
Nifty100
│
├── data/
│   ├── raw/
│   └── supporting/
│
├── db/
│   └── nifty100.db
│
├── docs/
│
├── output/
│
├── reports/
│
├── scripts/
│
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
│
├── tests/
│
└── README.md
```

---

## Dashboard Modules

- Home Dashboard
- Company Profile
- Stock Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation
- Reports & Tearsheet Viewer

---

## Installation

### Clone the repository

```bash
git clone <repository-url>
cd Nifty100
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Project

### Run the ETL Pipeline

```bash
python src/etl/load_to_sqlite.py
```

### Generate Financial Ratios

```bash
python src/ratios/populate_financial_ratios.py
```

### Start the FastAPI Server

```bash
uvicorn src.api.main:app --reload
```

API Documentation

```
http://127.0.0.1:8000/docs
```

### Launch the Dashboard

```bash
streamlit run src/dashboard/app.py
```

Dashboard

```
http://localhost:8501
```

---

## Testing

Run the complete test suite

```bash
python -m pytest tests/
```

Run code quality checks

```bash
python -m ruff check src/ tests/
```

Format the project

```bash
black src/ tests/
```

---

## Project Outputs

The project generates the following outputs:

- Financial ratio database
- Company PDF tearsheets
- Stock screener reports
- Peer comparison reports
- Sector analysis reports
- Valuation summaries
- Cash flow intelligence reports
- Capital allocation reports
- Performance reports
- Validation reports

---

## Documentation

Project documentation is available in the `docs/` directory and includes:

- Project Report
- Analyst Guide
- OpenAPI Specification
- Postman Collection

---

## Project Status

Completed as part of an Agile sprint-based development workflow, covering:

- Data Engineering
- Financial Analytics
- API Development
- Dashboard Development
- Testing and Validation
- Performance Optimization
- Documentation

---

## License

This project is intended for educational and research purposes.