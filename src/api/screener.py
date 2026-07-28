
import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from src.api.app import get_connection

router = APIRouter(
    prefix="/screener",
    tags=["Screener"],
)


@router.get("/")
def screener(
    min_roe: float | None = Query(None),
    max_de: float | None = Query(None),
    min_fcf: float | None = Query(None),
    sector: str | None = Query(None),
    min_rev_cagr_5yr: float | None = Query(None),
    min_pat_cagr_5yr: float | None = Query(None),
    max_pe: float | None = Query(None),
):

    if min_roe is not None and min_roe < 0:
        raise HTTPException(400, "min_roe must be >= 0")

    if max_de is not None and max_de < 0:
        raise HTTPException(400, "max_de must be >= 0")

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
        fr.pe_ratio,
        fr.composite_quality_score

    FROM financial_ratios fr

    INNER JOIN
    (
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

    if max_pe is not None and "pe_ratio" in df.columns:
        df = df[df["pe_ratio"] <= max_pe]

    if "composite_quality_score" in df.columns:
        df = df.sort_values(
            "composite_quality_score",
            ascending=False,
        )

    df = df.astype(object).where(pd.notna(df), None)

    return {
        "count": len(df),
        "results": df.to_dict(orient="records"),
    }
