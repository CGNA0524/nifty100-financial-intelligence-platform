import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "reports" / "sector"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()

TITLE_STYLE = styles["Title"]
HEADING_STYLE = styles["Heading2"]
BODY_STYLE = styles["BodyText"]

TITLE_STYLE.alignment = TA_CENTER


# =====================================================
# Database Connection
# =====================================================


def get_connection():

    return sqlite3.connect(DB_PATH)


# =====================================================
# Load Sector Data
# =====================================================


def load_sector_data():

    conn = get_connection()

    query = """
    SELECT

        c.id,
        c.company_name,

        s.broad_sector,
        s.sub_sector,
        s.market_cap_category,

        c.roe_percentage,
        c.roce_percentage,

        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,

        fr.debt_to_equity,
        fr.free_cash_flow_cr,

        fr.composite_quality_score,

        fr.year

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

    ORDER BY

        s.broad_sector,
        c.company_name
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# =====================================================
# Sector Summary
# =====================================================


def build_sector_summary(df):

    summary = (
        df.groupby("broad_sector")
        .agg(
            total_companies=("id", "count"),
            median_roe=("roe_percentage", "median"),
            median_roce=("roce_percentage", "median"),
            median_revenue_cagr=("revenue_cagr_5yr", "median"),
            median_pat_cagr=("pat_cagr_5yr", "median"),
            median_debt_to_equity=("debt_to_equity", "median"),
            median_fcf=("free_cash_flow_cr", "median"),
            median_quality=("composite_quality_score", "median"),
        )
        .reset_index()
    )

    summary = summary.round(2)

    return summary


# =====================================================
# Sector Companies
# =====================================================


def get_sector_companies(df, sector):

    sector_df = df[df["broad_sector"] == sector].copy().sort_values(by="company_name")

    sector_df = sector_df[
        [
            "company_name",
            "roe_percentage",
            "roce_percentage",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "debt_to_equity",
            "free_cash_flow_cr",
            "composite_quality_score",
        ]
    ]

    sector_df = sector_df.round(2)

    sector_df = sector_df.fillna("-")

    return sector_df


# =====================================================
# Sector List
# =====================================================


def get_all_sectors(df):

    return sorted(df["broad_sector"].dropna().unique().tolist())


# =====================================================
# PDF Header
# =====================================================


def build_header(sector_name):

    header = Table(
        [
            [
                Paragraph(
                    f"""
                <font color="white" size="22">
                <b>{sector_name}</b><br/>
                Sector Intelligence Report
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
# KPI Summary Table
# =====================================================


def build_summary_table(summary_row):

    data = [
        ["Metric", "Value"],
        ["Companies", summary_row["total_companies"]],
        ["Median ROE (%)", summary_row["median_roe"]],
        ["Median ROCE (%)", summary_row["median_roce"]],
        ["Median Revenue CAGR (%)", summary_row["median_revenue_cagr"]],
        ["Median PAT CAGR (%)", summary_row["median_pat_cagr"]],
        ["Median Debt / Equity", summary_row["median_debt_to_equity"]],
        ["Median Free Cash Flow", summary_row["median_fcf"]],
        ["Median Quality Score", summary_row["median_quality"]],
    ]

    table = Table(data, colWidths=[3.8 * inch, 2.0 * inch])

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B1F3A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
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
# Company Table
# =====================================================


def build_company_table(df):

    data = [["Company", "ROE", "ROCE", "Rev CAGR", "PAT CAGR", "D/E", "FCF", "Quality"]]

    for _, row in df.iterrows():

        data.append(
            [
                Paragraph(str(row["company_name"]), BODY_STYLE),
                row["roe_percentage"],
                row["roce_percentage"],
                row["revenue_cagr_5yr"],
                row["pat_cagr_5yr"],
                row["debt_to_equity"],
                row["free_cash_flow_cr"],
                row["composite_quality_score"],
            ]
        )

    table = Table(
        data,
        colWidths=[
            2.15 * inch,
            0.60 * inch,
            0.60 * inch,
            0.75 * inch,
            0.75 * inch,
            0.55 * inch,
            0.75 * inch,
            0.80 * inch,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("WORDWRAP", (0, 0), (-1, -1), True),
            ]
        )
    )

    return table


# =====================================================
# Generate Sector PDF
# =====================================================


def generate_sector_pdf(sector_name, summary_row, company_df):

    pdf_path = OUTPUT_DIR / f"{sector_name}_report.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.50 * inch,
        bottomMargin=0.50 * inch,
    )

    story = []

    # =====================================================
    # Header
    # =====================================================

    story.append(build_header(sector_name))

    story.append(Spacer(1, 0.25 * inch))

    # =====================================================
    # Summary
    # =====================================================

    story.append(Paragraph("<b>Sector Summary</b>", HEADING_STYLE))

    story.append(Spacer(1, 0.10 * inch))

    story.append(build_summary_table(summary_row))

    story.append(Spacer(1, 0.30 * inch))

    # =====================================================
    # Company Metrics
    # =====================================================

    story.append(Paragraph("<b>Companies</b>", HEADING_STYLE))

    story.append(Spacer(1, 0.10 * inch))

    story.append(build_company_table(company_df))

    story.append(Spacer(1, 0.20 * inch))

    doc.build(story)

    print(f"Generated : {pdf_path.name}")


# =====================================================
# Main
# =====================================================


def main():

    print("=" * 60)
    print("Sprint 5 - Day 34")
    print("Sector PDF Report Generator")
    print("=" * 60)

    df = load_sector_data()

    print(f"\nRows Loaded : {len(df)}")

    summary = build_sector_summary(df)

    sectors = get_all_sectors(df)

    print(f"Sectors Found : {len(sectors)}\n")

    for sector in sectors:

        print("-" * 60)
        print(f"Processing : {sector}")

        summary_row = summary[summary["broad_sector"] == sector].iloc[0]

        company_df = get_sector_companies(df, sector)

        generate_sector_pdf(
            sector_name=sector, summary_row=summary_row, company_df=company_df
        )

    print("\n" + "=" * 60)
    print("Sector Report Generation Complete")
    print("=" * 60)
    print(f"\nReports Saved To:\n{OUTPUT_DIR}")


if __name__ == "__main__":
    main()
