from pathlib import Path
import sqlite3
import tempfile

import pandas as pd
import matplotlib.pyplot as plt

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output" / "tearsheets"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()

TITLE_STYLE = styles["Title"]
HEADING_STYLE = styles["Heading2"]
BODY_STYLE = styles["BodyText"]

TITLE_STYLE.alignment = TA_CENTER

def get_connection():
    return sqlite3.connect(DB_PATH)


def load_companies():

    conn = get_connection()

    query = """
    SELECT
        id,
        company_name,
        website,
        face_value,
        book_value,
        roe_percentage,
        roce_percentage
    FROM companies
    ORDER BY id
    """

    companies = pd.read_sql(query, conn)

    conn.close()

    return companies

def load_pros_cons():

    file = PROJECT_ROOT / "output" / "pros_cons_generated.csv"

    df = pd.read_csv(file)

    return df

def load_cashflow():

    file = PROJECT_ROOT / "output" / "cashflow_intelligence.xlsx"

    df = pd.read_excel(file)

    return df

def load_profit_loss(company_id):

    conn = get_connection()

    query = """
    SELECT
        year,
        sales,
        net_profit
    FROM profitandloss
    WHERE company_id = ?
    ORDER BY year
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company_id]
    )

    conn.close()

    return df

def load_balance_sheet(company_id):

    conn = get_connection()

    query = """
    SELECT
        year,
        equity_capital,
        reserves,
        borrowings,
        other_liabilities,
        total_liabilities
    FROM balancesheet
    WHERE company_id = ?
    ORDER BY year
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company_id]
    )

    conn.close()

    return df

def load_financial_ratios(company_id):

    conn = get_connection()

    query = """
    SELECT
        year,
        return_on_equity_pct,
        operating_profit_margin_pct,
        debt_to_equity,
        interest_coverage,
        free_cash_flow_cr,
        earnings_per_share,
        book_value_per_share,
        revenue_cagr_5yr,
        pat_cagr_5yr,
        eps_cagr_5yr,
        composite_quality_score
    FROM financial_ratios
    WHERE company_id = ?
    ORDER BY year
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company_id]
    )

    conn.close()

    return df

def load_capital_allocation(company_id):

    file = PROJECT_ROOT / "output" / "capital_allocation.csv"

    df = pd.read_csv(file)

    df = df[df["company_id"] == company_id]

    return df


def create_revenue_chart(df, company_id):

    if df.empty:
        return None

    chart_path = OUTPUT_DIR / f"temp_revenue_{company_id}.png"

    plt.figure(figsize=(6, 3))

    plt.plot(
        df["year"].astype(str),
        df["sales"],
        marker="o",
        linewidth=2
    )

    plt.title("Revenue Trend")

    plt.xlabel("Year")

    plt.ylabel("Sales")

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(chart_path)

    plt.close()

    return chart_path

def create_net_profit_chart(df, company_id):

    if df.empty:
        return None

    chart_path = OUTPUT_DIR / f"temp_netprofit_{company_id}.png"

    plt.figure(figsize=(6, 3))

    plt.bar(
        df["year"].astype(str),
        df["net_profit"]
    )

    plt.title("Net Profit Trend")

    plt.xlabel("Year")

    plt.ylabel("Net Profit")

    plt.grid(axis="y")

    plt.tight_layout()

    plt.savefig(chart_path)

    plt.close()

    return chart_path

def create_roe_roce_chart(company, company_id):

    chart_path = OUTPUT_DIR / f"temp_roe_roce_{company_id}.png"

    labels = ["ROE", "ROCE"]

    values = [
        company["roe_percentage"],
        company["roce_percentage"]
    ]

    plt.figure(figsize=(4.5, 3))

    plt.bar(
        labels,
        values,
        width=0.5
    )

    plt.title("ROE vs ROCE")

    plt.ylabel("Percentage")

    plt.grid(axis="y")

    plt.tight_layout()

    plt.savefig(chart_path)

    plt.close()

    return chart_path

def create_balance_sheet_chart(df, company_id):

    if df.empty:
        return None

    chart_path = OUTPUT_DIR / f"temp_balance_sheet_{company_id}.png"

    years = df["year"].astype(str)

    plt.figure(figsize=(6, 3.5))

    plt.bar(
        years,
        df["equity_capital"],
        label="Equity"
    )

    plt.bar(
        years,
        df["reserves"],
        bottom=df["equity_capital"],
        label="Reserves"
    )

    plt.bar(
        years,
        df["borrowings"],
        bottom=df["equity_capital"] + df["reserves"],
        label="Borrowings"
    )

    plt.bar(
        years,
        df["other_liabilities"],
        bottom=(
            df["equity_capital"]
            + df["reserves"]
            + df["borrowings"]
        ),
        label="Other Liabilities"
    )

    plt.title("Balance Sheet Composition")

    plt.xlabel("Year")
    plt.ylabel("Amount")

    plt.xticks(rotation=45)

    plt.legend(fontsize=8)

    plt.tight_layout()

    plt.savefig(chart_path)

    plt.close()

    return chart_path

def build_header(company_name, ticker):

    data = [[
        Paragraph(
            f"""
            <font color="white" size="20">
            <b>{company_name}</b><br/>
            <font size="12">{ticker}</font>
            </font>
            """,
            BODY_STYLE
        )
    ]]

    table = Table(
        data,
        colWidths=[7.2 * inch]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0B1F3A")),
            ("LEFTPADDING", (0, 0), (-1, -1), 15),
            ("RIGHTPADDING", (0, 0), (-1, -1), 15),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )

    return table

def build_kpi_tiles(company, ratios):

    latest = ratios.iloc[-1] if not ratios.empty else None

    def value(v):
        if v is None or pd.isna(v):
            return "N/A"
        return f"{v:.2f}"

    data = [
        [
            f"<b>ROE</b><br/>{value(company['roe_percentage'])}%",
            f"<b>ROCE</b><br/>{value(company['roce_percentage'])}%",
            f"<b>Book Value</b><br/>{value(company['book_value'])}"
        ],
        [
            f"<b>Face Value</b><br/>{value(company['face_value'])}",
            f"<b>Revenue CAGR</b><br/>{value(latest['revenue_cagr_5yr']) if latest is not None else 'N/A'}%",
            f"<b>Quality Score</b><br/>{value(latest['composite_quality_score']) if latest is not None else 'N/A'}"
        ]
    ]

    table = Table(
        data,
        colWidths=[2.35 * inch] * 3,
        rowHeights=[0.75 * inch] * 2
    )

    table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.white),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF2FF")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ])
    )

    return table


def main():

    print("=" * 60)
    print("Sprint 5 - Day 33")
    print("Company PDF Tearsheet")
    print("=" * 60)

    companies = load_companies()
    pros_cons = load_pros_cons()
    cashflow = load_cashflow()

    print(f"\nCompanies Found : {len(companies)}")

    for _, company in companies.iterrows():

        company_id = company["id"]
        company_name = company["company_name"]

        pdf_path = OUTPUT_DIR / f"{company_id}.pdf"

        doc = SimpleDocTemplate(str(pdf_path))

        story = []

        # ====================================================
        # Load Data
        # ====================================================

        profit_loss = load_profit_loss(company_id)
        balance_sheet = load_balance_sheet(company_id)
        ratios = load_financial_ratios(company_id)

        revenue_chart = create_revenue_chart(
            profit_loss,
            company_id
        )

        net_profit_chart = create_net_profit_chart(
            profit_loss,
            company_id
        )

        roe_roce_chart = create_roe_roce_chart(
            company,
            company_id
        )

        balance_sheet_chart = create_balance_sheet_chart(
            balance_sheet,
            company_id
        )

        # ====================================================
        # Header
        # ====================================================

        story.append(
            build_header(
                company_name,
                company_id
            )
        )

        story.append(Spacer(1, 0.18 * inch))

        # ====================================================
        # KPI Tiles
        # ====================================================

        story.append(
            build_kpi_tiles(
                company,
                ratios
            )
        )

        story.append(Spacer(1, 0.25 * inch))

        # ====================================================
        # Revenue Trend
        # ====================================================

        if revenue_chart is not None:

            story.append(
                Paragraph(
                    "<b>Revenue Trend</b>",
                    HEADING_STYLE
                )
            )

            story.append(
                Image(
                    str(revenue_chart),
                    width=6.2 * inch,
                    height=3.0 * inch
                )
            )

            story.append(
                Spacer(
                    1,
                    0.20 * inch
                )
            )

        # ====================================================
        # Net Profit Trend
        # ====================================================

        if net_profit_chart is not None:

            story.append(
                Paragraph(
                    "<b>Net Profit Trend</b>",
                    HEADING_STYLE
                )
            )

            story.append(
                Image(
                    str(net_profit_chart),
                    width=6.2 * inch,
                    height=3.0 * inch
                )
            )

            story.append(
                Spacer(
                    1,
                    0.20 * inch
                )
            )

        # ====================================================
        # ROE vs ROCE
        # ====================================================

        if roe_roce_chart is not None:

            story.append(
                Paragraph(
                    "<b>ROE vs ROCE</b>",
                    HEADING_STYLE
                )
            )

            story.append(
                Image(
                    str(roe_roce_chart),
                    width=5.0 * inch,
                    height=3.2 * inch
                )
            )

            story.append(
                Spacer(
                    1,
                    0.20 * inch
                )
            )

        # ====================================================
        # Balance Sheet Composition
        # ====================================================

        if balance_sheet_chart is not None:

            story.append(
                Paragraph(
                    "<b>Balance Sheet Composition</b>",
                    HEADING_STYLE
                )
            )

            story.append(
                Image(
                    str(balance_sheet_chart),
                    width=6.2 * inch,
                    height=3.4 * inch
                )
            )

            story.append(
                Spacer(
                    1,
                    0.20 * inch
                )
            )

        # ====================================================
        # Pros & Cons
        # ====================================================

        pc = pros_cons[pros_cons["company_id"] == company_id]

        if not pc.empty:

            story.append(
                Paragraph(
                    "<b>Pros</b>",
                    HEADING_STYLE
                )
            )

            story.append(
                Paragraph(
                    str(pc.iloc[0]["pros"]),
                    BODY_STYLE
                )
            )

            story.append(
                Spacer(
                    1,
                    0.10 * inch
                )
            )

            story.append(
                Paragraph(
                    "<b>Cons</b>",
                    HEADING_STYLE
                )
            )

            story.append(
                Paragraph(
                    str(pc.iloc[0]["cons"]),
                    BODY_STYLE
                )
            )

            story.append(
                Spacer(
                    1,
                    0.20 * inch
                )
            )

        # ====================================================
        # Cash Flow Intelligence
        # ====================================================

        cf = cashflow[cashflow["company_id"] == company_id]

        if not cf.empty:

            story.append(
                Paragraph(
                    "<b>Cash Flow Intelligence</b>",
                    HEADING_STYLE
                )
            )

            story.append(
                Paragraph(
                    str(cf.iloc[0]["cashflow_insights"]),
                    BODY_STYLE
                )
            )

            story.append(
                Spacer(
                    1,
                    0.20 * inch
                )
            )

        doc.build(story)

        if revenue_chart is not None and revenue_chart.exists():
            revenue_chart.unlink()

        if net_profit_chart is not None and net_profit_chart.exists():
            net_profit_chart.unlink()

        if roe_roce_chart is not None and roe_roce_chart.exists():
            roe_roce_chart.unlink()

        if balance_sheet_chart is not None and balance_sheet_chart.exists():
            balance_sheet_chart.unlink()

    print(f"\nPDFs Generated : {len(companies)}")
    print("\nSaved To:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()