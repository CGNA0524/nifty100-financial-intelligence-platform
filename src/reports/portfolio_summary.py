import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
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

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "reports" / "portfolio"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "portfolio_summary.pdf"

styles = getSampleStyleSheet()

TITLE_STYLE = styles["Title"]
TITLE_STYLE.alignment = TA_CENTER

HEADING_STYLE = styles["Heading2"]
BODY_STYLE = styles["BodyText"]


# =====================================================
# Database Connection
# =====================================================


def get_connection():

    return sqlite3.connect(DB_PATH)


# =====================================================
# Load Portfolio Data
# =====================================================


def load_portfolio():

    conn = get_connection()

    query = """
    SELECT

        c.id,
        c.company_name,

        s.broad_sector,
        s.sub_sector,
        s.market_cap_category,

        c.face_value,
        c.book_value,
        c.roe_percentage,
        c.roce_percentage,

        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.eps_cagr_5yr,
        fr.debt_to_equity,
        fr.composite_quality_score

    FROM companies c

    LEFT JOIN sectors s
        ON c.id = s.company_id

    LEFT JOIN financial_ratios fr
        ON c.id = fr.company_id

    WHERE fr.year = (

        SELECT MAX(year)

        FROM financial_ratios f2

        WHERE f2.company_id = fr.company_id

    )

    ORDER BY c.company_name
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# =====================================================
# Trend Arrow
# =====================================================


def get_trend_arrow(value):

    if pd.isna(value):
        return "-"

    if value > 2:
        return "↑"

    elif value < -2:
        return "↓"

    return "→"


# =====================================================
# Format Value
# =====================================================


def format_value(value, suffix=""):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}{suffix}"


# =====================================================
# Build KPI Table
# =====================================================


def build_kpi_table(company):

    data = [
        ["Metric", "Value"],
        ["Sector", company["broad_sector"]],
        ["Sub Sector", company["sub_sector"]],
        ["Market Cap", company["market_cap_category"]],
        ["ROE", format_value(company["roe_percentage"], "%")],
        ["ROCE", format_value(company["roce_percentage"], "%")],
        [
            "Revenue CAGR",
            f"{format_value(company['revenue_cagr_5yr'],'%')} "
            f"{get_trend_arrow(company['revenue_cagr_5yr'])}",
        ],
        [
            "PAT CAGR",
            f"{format_value(company['pat_cagr_5yr'],'%')} "
            f"{get_trend_arrow(company['pat_cagr_5yr'])}",
        ],
        [
            "EPS CAGR",
            f"{format_value(company['eps_cagr_5yr'],'%')} "
            f"{get_trend_arrow(company['eps_cagr_5yr'])}",
        ],
        ["Debt / Equity", format_value(company["debt_to_equity"])],
        ["Quality Score", format_value(company["composite_quality_score"])],
        ["Book Value", format_value(company["book_value"])],
        ["Face Value", format_value(company["face_value"])],
    ]

    table = Table(data, colWidths=[2.8 * inch, 3.8 * inch])

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B1F3A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("WORDWRAP", (0, 0), (-1, -1), True),
            ]
        )
    )

    return table


# =====================================================
# PDF Header
# =====================================================


def build_header(company):

    header = Table(
        [
            [
                Paragraph(
                    f"""
                <font color="white" size="22">
                <b>{company['company_name']}</b><br/>
                Portfolio Summary
                </font>
                """,
                    BODY_STYLE,
                )
            ]
        ],
        colWidths=[7.2 * inch],
    )

    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0B1F3A")),
                ("LEFTPADDING", (0, 0), (-1, -1), 15),
                ("RIGHTPADDING", (0, 0), (-1, -1), 15),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    return header


# =====================================================
# Company Page
# =====================================================


def build_company_page(company):

    story = []

    story.append(build_header(company))

    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("<b>Company Overview</b>", HEADING_STYLE))

    story.append(Spacer(1, 0.10 * inch))

    story.append(build_kpi_table(company))

    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("<b>Top 6 KPIs</b>", HEADING_STYLE))

    story.append(Spacer(1, 0.10 * inch))

    kpis = [
        f"• ROE : {format_value(company['roe_percentage'],'%')}",
        f"• ROCE : {format_value(company['roce_percentage'],'%')}",
        f"• Revenue CAGR : {format_value(company['revenue_cagr_5yr'],'%')} {get_trend_arrow(company['revenue_cagr_5yr'])}",
        f"• PAT CAGR : {format_value(company['pat_cagr_5yr'],'%')} {get_trend_arrow(company['pat_cagr_5yr'])}",
        f"• EPS CAGR : {format_value(company['eps_cagr_5yr'],'%')} {get_trend_arrow(company['eps_cagr_5yr'])}",
        f"• Quality Score : {format_value(company['composite_quality_score'])}",
    ]

    for item in kpis:

        story.append(Paragraph(item, BODY_STYLE))

    story.append(Spacer(1, 0.20 * inch))

    return story


# =====================================================
# Generate Portfolio PDF
# =====================================================


def generate_portfolio_pdf(df):

    doc = SimpleDocTemplate(
        str(OUTPUT_FILE),
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.50 * inch,
        bottomMargin=0.50 * inch,
    )

    story = []

    total_companies = len(df)

    for index, (_, company) in enumerate(df.iterrows()):

        print(
            f"Generating : {company['company_name']} "
            f"({index + 1}/{total_companies})"
        )

        company_story = build_company_page(company)

        story.extend(company_story)

        if index != total_companies - 1:

            story.append(PageBreak())

    doc.build(story)

    print("\nPortfolio PDF Generated Successfully")

    print(f"\nSaved To:\n{OUTPUT_FILE}")


# =====================================================
# Main
# =====================================================


def main():

    print("=" * 60)
    print("Sprint 5 - Day 35")
    print("Portfolio Summary PDF")
    print("=" * 60)

    portfolio = load_portfolio()

    print(f"\nCompanies Loaded : {len(portfolio)}")

    portfolio = portfolio.sort_values(by="company_name").reset_index(drop=True)

    portfolio["roe_percentage"] = portfolio["roe_percentage"].round(2)

    portfolio["roce_percentage"] = portfolio["roce_percentage"].round(2)

    portfolio["revenue_cagr_5yr"] = portfolio["revenue_cagr_5yr"].round(2)

    portfolio["pat_cagr_5yr"] = portfolio["pat_cagr_5yr"].round(2)

    portfolio["eps_cagr_5yr"] = portfolio["eps_cagr_5yr"].round(2)

    portfolio["debt_to_equity"] = portfolio["debt_to_equity"].round(2)

    portfolio["composite_quality_score"] = portfolio["composite_quality_score"].round(2)

    generate_portfolio_pdf(portfolio)

    print("\n" + "=" * 60)
    print("Portfolio Summary Generation Complete")
    print("=" * 60)

    print(f"\nTotal Companies : {len(portfolio)}")

    print(f"\nOutput File :\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
