import sqlite3
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

from src.api.exceptions import register_exception_handlers
from src.api.middleware import ProcessTimeMiddleware

# ==========================================================
# Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

# ==========================================================
# FastAPI App
# ==========================================================

app = FastAPI(
    title="Nifty100 Financial Intelligence API",
    description="REST API for financial analytics, clustering and valuation.",
    version="1.0.0",
)
app.add_middleware(ProcessTimeMiddleware)
register_exception_handlers(app)

# ==========================================================
# Database Connection
# ==========================================================


def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================================
# Root Endpoint
# ==========================================================


@app.get("/")
def root():

    return {
        "message": "Nifty100 Financial Intelligence API",
        "status": "running",
        "version": "1.0.0",
    }


# ==========================================================
# Health Check
# ==========================================================


@app.get("/health")
def health():

    try:

        conn = get_connection()

        conn.execute("SELECT 1")

        conn.close()

        return {"database": "connected", "status": "healthy"}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


from fastapi.encoders import jsonable_encoder

# ==========================================================
# Companies Endpoint
# ==========================================================


@app.get("/companies")
def get_companies():

    try:

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
        ORDER BY company_name
        """

        df = pd.read_sql(query, conn)

        conn.close()

        # Convert NaN -> None
        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records)

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Company Details
# ==========================================================


@app.get("/company/{company_id}")
def get_company(company_id: str):

    try:

        conn = get_connection()

        query = """
        SELECT *
        FROM companies
        WHERE id = ?
        """

        df = pd.read_sql(query, conn, params=[company_id])

        conn.close()

        if df.empty:

            raise HTTPException(status_code=404, detail="Company not found")

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records[0])

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Financial Ratios
# ==========================================================


@app.get("/financial-ratios/{company_id}")
def get_financial_ratios(company_id: str):

    try:

        conn = get_connection()

        query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year DESC
        """

        df = pd.read_sql(query, conn, params=[company_id])

        conn.close()

        if df.empty:

            raise HTTPException(status_code=404, detail="Financial ratios not found")

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Cluster Results
# ==========================================================


@app.get("/clusters")
def get_clusters():

    try:

        file_path = PROJECT_ROOT / "output" / "cluster_labels.csv"

        df = pd.read_csv(file_path)

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records)

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Cluster Profile Summary
# ==========================================================


@app.get("/cluster-summary")
def get_cluster_summary():

    try:

        file_path = PROJECT_ROOT / "output" / "cluster_profile_summary.csv"

        df = pd.read_csv(file_path)

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records)

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Screener Endpoint
# ==========================================================


@app.get("/screener")
def screener(
    min_roe: float | None = None,
    max_de: float | None = None,
    min_fcf: float | None = None,
    sector: str | None = None,
    min_rev_cagr_5yr: float | None = None,
    min_pat_cagr_5yr: float | None = None,
    max_pe: float | None = None,
):

    try:

        conn = get_connection()

        query = """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,

            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.free_cash_flow_cr,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            fr.composite_quality_score

        FROM financial_ratios fr

        INNER JOIN (
            SELECT company_id,
                   MAX(year) latest_year
            FROM financial_ratios
            GROUP BY company_id
        ) latest

        ON fr.company_id = latest.company_id
        AND fr.year = latest.latest_year

        LEFT JOIN companies c
            ON fr.company_id = c.id

        LEFT JOIN sectors s
            ON fr.company_id = s.company_id
        """

        df = pd.read_sql(query, conn)

        conn.close()

        if min_roe is not None:
            df = df[df["return_on_equity_pct"] >= min_roe]

        if max_de is not None:
            df = df[df["debt_to_equity"] <= max_de]

        if min_fcf is not None:
            df = df[df["free_cash_flow_cr"] >= min_fcf]

        if sector:
            df = df[df["broad_sector"].str.lower() == sector.lower()]

        if min_rev_cagr_5yr is not None:
            df = df[df["revenue_cagr_5yr"] >= min_rev_cagr_5yr]

        if min_pat_cagr_5yr is not None:
            df = df[df["pat_cagr_5yr"] >= min_pat_cagr_5yr]

        if "composite_quality_score" in df.columns:
            df = df.sort_values("composite_quality_score", ascending=False)

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder({"count": len(records), "results": records})

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Profit & Loss History
# ==========================================================


@app.get("/companies/{company_id}/pl")
def get_profit_loss(
    company_id: str,
    from_year: int | None = None,
    to_year: int | None = None,
):

    try:

        conn = get_connection()

        query = """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        """

        params = [company_id]

        if from_year is not None:
            query += " AND year >= ?"
            params.append(from_year)

        if to_year is not None:
            query += " AND year <= ?"
            params.append(to_year)

        query += " ORDER BY year DESC"

        df = pd.read_sql(query, conn, params=params)

        conn.close()

        if df.empty:

            raise HTTPException(status_code=404, detail="Profit & Loss data not found")

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Balance Sheet History
# ==========================================================


@app.get("/companies/{company_id}/bs")
def get_balance_sheet(
    company_id: str,
    from_year: int | None = None,
    to_year: int | None = None,
):

    try:

        conn = get_connection()

        query = """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        """

        params = [company_id]

        if from_year is not None:
            query += " AND year >= ?"
            params.append(from_year)

        if to_year is not None:
            query += " AND year <= ?"
            params.append(to_year)

        query += " ORDER BY year DESC"

        df = pd.read_sql(query, conn, params=params)

        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="Balance Sheet not found")

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Cash Flow History
# ==========================================================


@app.get("/companies/{company_id}/cashflow")
def get_cashflow(
    company_id: str,
    from_year: int | None = None,
    to_year: int | None = None,
):

    try:

        conn = get_connection()

        query = """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        """

        params = [company_id]

        if from_year is not None:
            query += " AND year >= ?"
            params.append(from_year)

        if to_year is not None:
            query += " AND year <= ?"
            params.append(to_year)

        query += " ORDER BY year DESC"

        df = pd.read_sql(query, conn, params=params)

        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="Cash Flow data not found")

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Market Cap & Valuation History
# ==========================================================


@app.get("/market-cap/{company_id}")
def get_market_cap(company_id: str):

    try:

        conn = get_connection()

        query = """
        SELECT
            company_id,
            year,
            market_cap_crore,
            enterprise_value_crore,
            pe_ratio,
            pb_ratio,
            ev_ebitda,
            dividend_yield_pct
        FROM market_cap
        WHERE company_id = ?
        ORDER BY year DESC
        """

        df = pd.read_sql(query, conn, params=[company_id])

        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="Market Cap data not found")

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# All Sectors
# ==========================================================


@app.get("/sectors")
def get_sectors():

    try:

        conn = get_connection()

        query = """
        SELECT
            broad_sector,
            COUNT(*) AS company_count
        FROM sectors
        GROUP BY broad_sector
        ORDER BY broad_sector
        """

        df = pd.read_sql(query, conn)

        conn.close()

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records)

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Companies in Sector
# ==========================================================


@app.get("/sectors/{sector}/companies")
def get_sector_companies(sector: str):

    try:

        conn = get_connection()

        query = """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            s.market_cap_category,
            s.index_weight_pct,

            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.revenue_cagr_5yr,
            fr.composite_quality_score

        FROM companies c

        INNER JOIN sectors s
            ON c.id = s.company_id

        LEFT JOIN financial_ratios fr
            ON c.id = fr.company_id

        WHERE LOWER(TRIM(s.broad_sector)) = LOWER(TRIM(?))

        GROUP BY
            c.id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            s.market_cap_category,
            s.index_weight_pct

        ORDER BY c.company_name
        """

        df = pd.read_sql(query, conn, params=[sector])

        conn.close()

        if df.empty:

            raise HTTPException(status_code=404, detail="Sector not found")

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Peer Group Endpoint
# ==========================================================

from urllib.parse import unquote


@app.get("/peers/{peer_group}")
def get_peer_group(peer_group: str):

    try:

        peer_group = unquote(peer_group).strip()

        conn = get_connection()

        query = """
        SELECT
            pg.peer_group_name,
            pg.company_id,
            pg.is_benchmark,
            c.company_name

        FROM peer_groups pg

        LEFT JOIN companies c
            ON pg.company_id = c.id

        WHERE LOWER(TRIM(pg.peer_group_name)) =
              LOWER(TRIM(?))

        ORDER BY c.company_name
        """

        df = pd.read_sql(query, conn, params=[peer_group])

        conn.close()

        if df.empty:
            raise HTTPException(
                status_code=404, detail=f"Peer group '{peer_group}' not found"
            )

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Annual Reports / Documents
# ==========================================================


@app.get("/companies/{company_id}/documents")
def get_documents(company_id: str):

    try:

        conn = get_connection()

        query = """
        SELECT
            company_id,
            Year,
            Annual_Report
        FROM documents
        WHERE company_id = ?
        ORDER BY Year DESC
        """

        df = pd.read_sql(query, conn, params=[company_id])

        conn.close()

        if df.empty:

            raise HTTPException(status_code=404, detail="Documents not found")

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Latest Financial Ratios
# ==========================================================


@app.get("/companies/{company_id}/ratios")
def get_latest_ratios(company_id: str):

    try:

        conn = get_connection()

        query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year DESC
        LIMIT 1
        """

        df = pd.read_sql(query, conn, params=[company_id])

        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="Financial ratios not found")

        records = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

        return jsonable_encoder(records[0])

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
