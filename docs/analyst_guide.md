# Nifty100 Financial Intelligence Platform
## Analyst Guide

Version: 1.0

---

# 1. Introduction

The Nifty100 Financial Intelligence Platform is an end-to-end financial analytics system built using Python, SQLite, FastAPI, and Streamlit. It provides financial ratio analysis, clustering, company intelligence, peer comparison, sector analysis, valuation metrics, portfolio analytics, and API access.

---

# 2. System Requirements

- Python 3.14+
- SQLite
- Streamlit
- FastAPI
- Pandas
- Plotly
- ReportLab

---

# 3. Installation

```bash
pip install -r requirements.txt
```

---

# 4. Database

Database:

```
db/nifty100.db
```

Contains financial information for 92 companies.

---

# 5. Running ETL

```bash
python src/etl/load_database.py
```

---

# 6. Running Analytics

```bash
python src/analytics/clustering.py
python src/analytics/cluster_profile.py
python src/analytics/correlation_heatmap.py
python src/analytics/outlier_detection.py
python src/analytics/portfolio_statistics.py
```

---

# 7. Running FastAPI

```bash
uvicorn src.api.app:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

---

# 8. Running Streamlit

```bash
streamlit run src/dashboard/app.py
```

---

# 9. Dashboard Overview

The dashboard provides:

- Company Profile
- Screener
- Peer Comparison
- Sector Intelligence
- Trends
- Reports
- Portfolio Analytics
- Capital Allocation

---

# 10. API Overview

The API provides endpoints for:

- Health
- Companies
- Ratios
- Screener
- Market Cap
- Sectors
- Peers
- Documents

---

# 11. Reports

Generated reports include:

- Portfolio Statistics
- Outlier Report
- Correlation Heatmap
- Cluster Profiles
- Executive Summary

---

# 12. Troubleshooting

- Verify database exists.
- Verify dependencies installed.
- Verify API is running.
- Verify Streamlit is running.

---

# 13. Testing

Run:

```bash
pytest -v
```

HTML Report:

```
reports/pytest_report.html
```

---

# 14. Performance

The platform supports concurrent API requests and completed the Sprint load-testing requirement successfully.

---

# 15. Conclusion

The platform provides a complete financial intelligence workflow including ETL, analytics, visualization, reporting, clustering, REST APIs, and dashboard support.