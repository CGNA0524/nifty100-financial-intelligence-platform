# Sprint 4 Retrospective

## Sprint Information

| Item | Details |
|------|---------|
| Sprint | Sprint 4 – Dashboard & Valuation Module |
| Duration | Day 22 – Day 28 |
| Target Story Points | 55 SP |
| Status | Completed |
| Developer | Chirag Nagra |

---

# Sprint Goal

The objective of Sprint 4 was to develop a complete interactive Streamlit dashboard for the Nifty 100 Financial Intelligence Platform and implement a valuation engine capable of analyzing all available companies using financial ratios and market capitalization data.

The dashboard was required to support multiple financial analysis screens while maintaining smooth navigation, fast loading times, and robust handling of incomplete financial data.

---

# Work Completed

## Dashboard Development

Successfully developed a multi-page Streamlit dashboard consisting of eight functional screens.

### Implemented Screens

- Home Dashboard
- Company Profile
- Stock Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation
- Annual Reports

All screens were integrated into a single Streamlit application with sidebar navigation.

---

# Database Integration

Implemented reusable cached database functions using Streamlit cache decorators.

Data loading includes:

- Company Information
- Profit & Loss
- Balance Sheet
- Cash Flow
- Financial Ratios
- Sector Data
- Peer Groups
- Valuation Data

Caching reduced repeated database queries and improved dashboard responsiveness.

---

# Home Dashboard

Implemented:

- Summary KPI cards
- Sector Distribution Donut Chart
- Top Companies Table
- Dynamic Year Selection

---

# Company Profile

Implemented:

- Company Search
- Company Information Card
- Financial KPI Tiles
- Revenue History
- Net Profit History
- ROE Trend
- ROCE Trend
- Pros & Cons Section
- Friendly "Ticker Not Found" handling
- Default Company Logo Support

---

# Stock Screener

Implemented:

- Live Financial Filtering
- Preset Screening Strategies
- Dynamic Result Count
- CSV Export
- Multiple Financial Metrics

---

# Peer Comparison

Implemented:

- Peer Group Selection
- Radar Chart Comparison
- KPI Benchmark Table

---

# Trend Analysis

Implemented:

- Multi-Metric Selection
- Historical Trend Visualization
- Financial Growth Analysis

---

# Sector Analysis

Implemented:

- Sector Selection
- Bubble Chart
- Sector KPI Comparison
- Company Distribution

---

# Capital Allocation

Implemented:

- Treemap Visualization
- Capital Allocation Categories
- Company Grouping

---

# Annual Reports

Implemented:

- Company Search
- Annual Report Links
- Missing Report Handling
- Report Availability Indicator

---

# Valuation Module

Developed the complete valuation engine.

Implemented calculations:

- Free Cash Flow Yield
- Sector Median P/E
- Relative P/E Comparison
- Discount Detection
- Fair Valuation Detection
- Overvaluation Detection

Generated outputs:

- valuation_summary.xlsx
- valuation_flags.csv

---

# Quality Assurance

Comprehensive testing was performed across all dashboard modules.

Testing included:

- Navigation testing
- Dashboard loading
- Company search
- Screener filtering
- CSV export
- Peer comparison
- Trend charts
- Sector charts
- Capital Allocation
- Annual Reports
- Valuation outputs

Testing was conducted using companies from multiple sectors including:

- Information Technology
- Banking & Financial Services
- FMCG
- Healthcare
- Energy
- Industrials

---

# UX Decisions

Several usability improvements were implemented during Sprint 4.

These include:

- Wide page layout for better visualization
- Sidebar navigation
- Interactive Plotly charts
- Friendly error messages
- Default company logo
- Dynamic filtering
- Search-based navigation
- CSV export functionality
- Consistent KPI card layout

These decisions improved usability and reduced user interaction time.

---

# Data Edge Cases Handled

The dashboard was designed to gracefully handle incomplete financial data.

Handled scenarios include:

- Missing financial ratios
- Missing annual reports
- Missing historical records
- Null database values
- Invalid ticker searches
- Companies with partial financial history

Instead of generating runtime exceptions, unavailable values are displayed as **N/A** wherever applicable.

---

# Bugs Fixed During Sprint

Several issues were identified and resolved during implementation.

Major fixes include:

- Latest financial year selection in Screener
- CSV export column consistency
- Bubble chart NaN handling
- Company logo rendering
- Plotly visualization issues
- Missing data handling
- Streamlit page integration
- Dashboard navigation improvements

These fixes significantly improved overall application stability.

---

# Performance Findings

Performance testing confirmed stable dashboard behavior.

Observations:

- Dashboard loads successfully
- Company Profile loads within expected response time
- Cached database queries reduce loading time
- Interactive charts render correctly
- No page crashes observed during testing
- Dashboard performs consistently across all implemented screens

---

# Challenges Faced

Some challenges encountered during development included:

- Handling inconsistent historical financial data
- Managing missing values during visualization
- Maintaining consistent financial year selection
- Plotly chart rendering issues
- Streamlit page integration
- Database query optimization

Each issue was resolved through validation, debugging, and iterative testing.

---

# Lessons Learned

Sprint 4 provided valuable experience in:

- Streamlit application development
- Dashboard design
- Interactive data visualization
- Financial analytics implementation
- SQLite integration
- Plotly chart customization
- Performance optimization
- Exception handling
- Software testing
- User experience improvements

---

# Deliverables Completed

- Streamlit Dashboard
- Eight Functional Screens
- Cached Database Layer
- Valuation Engine
- CSV Export
- Valuation Reports
- Financial Analytics
- Interactive Charts
- Documentation
- Testing

---

# Sprint Outcome

Sprint 4 objectives were successfully achieved.

The dashboard is capable of analyzing all available Nifty 100 companies through multiple analytical views while providing valuation insights and interactive financial visualizations.

All major deliverables defined in Sprint 4 were completed successfully, and the project is ready to proceed to the next development sprint.

---

# Sprint Status

**Sprint 4 Successfully Completed**

**Overall Completion:** **100%**

**Project Status:** Ready for Sprint 5