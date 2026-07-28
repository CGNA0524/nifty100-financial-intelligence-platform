import sqlite3

import pandas as pd
import streamlit as st

DB_PATH = "db/nifty100.db"


# ==========================================
# Companies
# ==========================================


@st.cache_data(ttl=600)
def get_companies():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM companies
        ORDER BY company_name
        """,
        conn,
    )

    conn.close()

    return df


# ==========================================
# All Financial Ratios
# ==========================================


@st.cache_data(ttl=600)
def get_all_ratios():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        ORDER BY company_id, year
        """,
        conn,
    )

    conn.close()

    return df


# ==========================================
# Company Ratios
# ==========================================


@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):

    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
    """

    params = [ticker]

    if year is not None:
        query += " AND year = ?"
        params.append(year)

    query += " ORDER BY year"

    df = pd.read_sql(query, conn, params=params)

    conn.close()

    return df


# ==========================================
# Profit & Loss
# ==========================================


@st.cache_data(ttl=600)
def get_pl(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df


# ==========================================
# Balance Sheet
# ==========================================


@st.cache_data(ttl=600)
def get_bs(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df


# ==========================================
# Cash Flow
# ==========================================


@st.cache_data(ttl=600)
def get_cf(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df


# ==========================================
# Sectors
# ==========================================


@st.cache_data(ttl=600)
def get_sectors():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM sectors
        ORDER BY broad_sector
        """,
        conn,
    )

    conn.close()

    return df


# ==========================================
# Peer Groups
# ==========================================


@st.cache_data(ttl=600)
def get_peers(group_name):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM peer_groups
        WHERE peer_group_name = ?
        """,
        conn,
        params=[group_name],
    )

    conn.close()

    return df


# ==========================================
# Valuation
# ==========================================


@st.cache_data(ttl=600)
def get_valuation(ticker):

    conn = sqlite3.connect(DB_PATH)

    tables = pd.read_sql(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        """,
        conn,
    )

    if "valuation" not in tables["name"].values:
        conn.close()
        return pd.DataFrame()

    df = pd.read_sql(
        """
        SELECT *
        FROM valuation
        WHERE company_id = ?
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_screener_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        fr.company_id,
        fr.year,
        c.company_name,
        s.broad_sector,

        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.interest_coverage,
        fr.free_cash_flow_cr,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.asset_turnover,
        fr.composite_quality_score

    FROM financial_ratios fr

    LEFT JOIN companies c
        ON fr.company_id = c.id

    LEFT JOIN sectors s
        ON fr.company_id = s.company_id
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_peer_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        pg.peer_group_name,
        fr.year,

        pg.company_id,

        c.company_name,

        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.asset_turnover,
        fr.interest_coverage,
        fr.free_cash_flow_cr,
        fr.composite_quality_score

    FROM peer_groups pg

    LEFT JOIN companies c
        ON pg.company_id = c.id

    LEFT JOIN financial_ratios fr
        ON pg.company_id = fr.company_id
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_trend_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        p.company_id,
        c.company_name,

        p.year,
        p.sales,
        p.net_profit,
        p.eps,

        fr.return_on_equity_pct,
        fr.operating_profit_margin_pct

    FROM profitandloss p

    LEFT JOIN companies c
        ON p.company_id = c.id

    LEFT JOIN financial_ratios fr
        ON p.company_id = fr.company_id
        AND p.year = fr.year

    ORDER BY
        p.company_id,
        p.year
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_sector_analysis():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        s.broad_sector,
        c.company_name,
        fr.year,

        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.composite_quality_score,
        fr.revenue_cagr_5yr

    FROM sectors s

    LEFT JOIN companies c
        ON s.company_id = c.id

    LEFT JOIN financial_ratios fr
        ON s.company_id = fr.company_id
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_capital_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        c.company_name,

        cf.company_id,
        cf.year,

        cf.operating_activity,
        cf.investing_activity,
        cf.financing_activity,

        fr.free_cash_flow_cr,
        fr.capex_cr

    FROM cashflow cf

    LEFT JOIN companies c
        ON cf.company_id = c.id

    LEFT JOIN financial_ratios fr
        ON cf.company_id = fr.company_id
        AND cf.year = fr.year

    ORDER BY
        cf.company_id,
        cf.year
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_report_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        c.company_name,
        p.company_id,
        p.year,

        p.sales,
        p.net_profit,
        p.eps,

        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.composite_quality_score,

        cf.operating_activity

    FROM profitandloss p

    LEFT JOIN companies c
        ON p.company_id = c.id

    LEFT JOIN financial_ratios fr
        ON p.company_id = fr.company_id
        AND p.year = fr.year

    LEFT JOIN cashflow cf
        ON p.company_id = cf.company_id
        AND p.year = cf.year

    ORDER BY
        p.company_id,
        p.year
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df
