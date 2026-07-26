# 📈 Nifty 100 Financial Intelligence Platform

A comprehensive financial analytics platform for Nifty 100 companies built using **Python, SQLite, Pandas, Plotly, and Streamlit**.

The platform provides company financial analysis, stock screening, peer comparison, trend analysis, sector insights, capital allocation visualization, annual report access, and valuation analysis through an interactive dashboard.

---

# Features

## Dashboard

- Home Dashboard
- Company Profile
- Stock Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation Map
- Annual Reports

---

## Financial Analytics

- 50+ Financial KPIs
- ROE
- ROCE
- Debt to Equity
- Revenue CAGR
- PAT CAGR
- Free Cash Flow
- Interest Coverage Ratio
- Asset Turnover
- Composite Quality Score

---

## Valuation Module

- Free Cash Flow Yield
- Sector Median P/E
- P/E Comparison
- Discount Detection
- Fair Valuation Detection
- Overvaluation Detection

Outputs generated:

- valuation_summary.xlsx
- valuation_flags.csv

---

# Technology Stack

- Python
- Streamlit
- Pandas
- SQLite
- Plotly
- NumPy

---

# Project Structure

```text
n100_financial_intelligence/

│

├── db/
│     └── nifty100.db
│
├── output/
│     ├── valuation_summary.xlsx
│     ├── valuation_flags.csv
│
├── src/
│
│     ├── analytics/
│     │      └── valuation.py
│     │
│     ├── dashboard/
│     │
│     │      ├── app.py
│     │      ├── assets/
│     │      ├── utils/
│     │      │      └── db.py
│     │      │
│     │      └── pages/
│     │             01_home.py
│     │             02_profile.py
│     │             03_screener.py
│     │             04_peers.py
│     │             05_trends.py
│     │             06_sectors.py
│     │             07_capital.py
│     │             08_reports.py
│
└── README.md
```

---

# Dashboard Screens

## 1. Home

Displays

- Total Companies
- Average ROE
- Median Debt/Equity
- Revenue CAGR
- Debt Free Companies
- Composite Quality Score
- Sector Distribution
- Top Quality Companies

---

## 2. Company Profile

Displays

- Company Information
- Financial KPIs
- Revenue Trend
- Net Profit Trend
- ROE & ROCE Trend
- Pros & Cons
- Company Overview

---

## 3. Stock Screener

Supports

- Custom Screening
- Quality Preset
- Growth Preset
- Value Preset
- Dividend Preset
- Debt Free Preset
- Turnaround Preset

Features

- Live Filtering
- CSV Export
- Multiple Financial Filters

---

## 4. Peer Comparison

Displays

- Peer Group Selection
- KPI Comparison
- Radar Chart
- Benchmark Comparison

---

## 5. Trend Analysis

Displays

- Revenue Trend
- Profit Trend
- ROE Trend
- Multi Metric Comparison
- Historical Financial Analysis

---

## 6. Sector Analysis

Displays

- Sector KPIs
- Bubble Chart
- Company Comparison
- Sector Performance

---

## 7. Capital Allocation

Displays

- Capital Allocation Categories
- Treemap Visualization
- Company Distribution

---

## 8. Annual Reports

Displays

- Annual Report Links
- Available Years
- Report Status
- Download Links

---

# Valuation Module

The valuation engine performs

- Free Cash Flow Yield Calculation
- Sector Median P/E Calculation
- P/E Comparison
- Discount Detection
- Fair Valuation Detection
- Overvaluation Detection

Generated files

```
output/

valuation_summary.xlsx

valuation_flags.csv
```

---

# Installation

Clone the repository

```bash
git clone <repository-url>
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Run Dashboard

```bash
streamlit run src/dashboard/app.py
```

---

# Valuation Module

```bash
python src/analytics/valuation.py
```

---

# Project Deliverables

- Interactive Streamlit Dashboard
- SQLite Database
- Financial Analytics Engine
- Stock Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation Map
- Annual Reports
- Valuation Module

---

# Outputs

```
valuation_summary.xlsx

valuation_flags.csv
```

---

# Testing

The project has been tested for

- Dashboard Navigation
- Company Profile
- Stock Screener
- CSV Export
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation
- Annual Reports
- Valuation Module

---

# Sprint 4 Completion

Completed Modules

- Dashboard Development
- Valuation Module
- Streamlit Integration
- Financial Analytics
- Testing
- Bug Fixes
- CSV Export
- Interactive Charts

---

# Author

**Chirag Nagra**

B.Tech Computer Engineering

Nifty 100 Financial Intelligence Platform

2026