from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch

styles = getSampleStyleSheet()

title_style = styles["Heading1"]
title_style.alignment = TA_CENTER

heading = styles["Heading2"]
body = styles["BodyText"]

doc = SimpleDocTemplate("docs/analyst_guide.pdf")

story = []

story.append(Paragraph("Nifty100 Financial Intelligence Platform", title_style))
story.append(Paragraph("Analyst Guide", heading))

sections = [
("1. Introduction",
"The Nifty100 Financial Intelligence Platform is a complete financial analytics solution developed using Python, SQLite, FastAPI and Streamlit. It provides company analysis, valuation, screening, clustering, peer comparison and portfolio analytics."),

("2. System Requirements",
"Python 3.14+, SQLite, Streamlit, FastAPI, Pandas, Plotly and ReportLab."),

("3. Installation",
"Install all dependencies using requirements.txt and create a virtual environment before execution."),

("4. Database",
"The platform uses db/nifty100.db containing financial information for 92 companies."),

("5. ETL",
"Execute the ETL pipeline to load and validate company financial statements."),

("6. Analytics",
"Generate KPIs, CAGR, clustering, correlation matrix, outlier reports and portfolio statistics."),

("7. Dashboard",
"The Streamlit dashboard provides Company Profile, Screener, Peer Comparison, Sector Intelligence, Trends and Reports."),

("8. FastAPI",
"The REST API exposes company data, ratios, screener, sectors, peers, valuation and documents."),

("9. Reports",
"Reports include executive summaries, portfolio summaries, valuation summaries and company tearsheets."),

("10. Testing",
"All automated tests are executed using pytest. The project currently passes all available tests."),

("11. Performance",
"Concurrent API load testing was successfully completed within the Sprint target."),

("12. Outputs",
"Generated outputs include cluster labels, outlier reports, portfolio statistics, heatmaps and OpenAPI specification."),

("13. Troubleshooting",
"Verify database path, dependencies and API server status if issues occur."),

("14. Best Practices",
"Always execute ETL before analytics. Regenerate reports after refreshing the database."),

("15. Conclusion",
"The project provides a complete financial intelligence platform suitable for equity research, screening, clustering and reporting.")
]

for title, text in sections:
    story.append(Paragraph("<br/><br/>", body))
    story.append(Paragraph(title, heading))
    story.append(Paragraph(text, body))

doc.build(story)

print("SUCCESS")
print("docs/analyst_guide.pdf created")