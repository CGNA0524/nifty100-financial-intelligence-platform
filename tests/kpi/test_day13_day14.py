"""Day 13 and Day 14 KPI tests."""

from __future__ import annotations

import pytest

from src.analytics.cagr import eps_cagr_5yr, pat_cagr_5yr, revenue_cagr_5yr
from src.analytics.ratio_engine import RatioEngine
from src.analytics.ratios import (
    asset_turnover,
    capex_intensity,
    debt_to_equity,
    fcf_conversion_rate,
    free_cash_flow,
    high_leverage_flag,
    interest_coverage_ratio,
    net_profit_margin,
    operating_profit_margin,
    return_on_assets,
    return_on_capital_employed,
    return_on_equity,
)


def build_synthetic_engine() -> RatioEngine:
    """Build a RatioEngine instance without touching the database."""

    engine = RatioEngine.__new__(RatioEngine)
    engine.records = []
    engine.ratio_results = []
    engine.company_history = {}
    return engine


def make_record(
    year: int, sales: float, net_profit: float, operating_profit: float
) -> dict:
    """Create a synthetic merged record for engine testing."""

    return {
        "company_id": "TESTCO",
        "year": f"Mar {year}",
        "pnl": {
            "sales": sales,
            "net_profit": net_profit,
            "operating_profit": operating_profit,
            "other_income": 0.0,
            "interest": 5.0,
            "eps": net_profit / 10,
            "dividend_payout": 12.5,
        },
        "balance": {
            "equity_capital": 100.0,
            "reserves": 100.0,
            "borrowings": 20.0,
            "total_assets": 300.0,
        },
        "cashflow": {
            "operating_activity": 30.0,
            "investing_activity": -10.0,
            "financing_activity": 5.0,
        },
        "company": {
            "book_value": 42.5,
        },
    }


def test_net_profit_margin() -> None:
    assert net_profit_margin(100, 1000) == 10.00


def test_net_profit_margin_zero_sales() -> None:
    assert net_profit_margin(100, 0) is None


def test_operating_profit_margin() -> None:
    assert operating_profit_margin(250, 1000) == 25.00


def test_return_on_equity() -> None:
    assert return_on_equity(100, 200, 300) == 20.00


def test_return_on_equity_negative_equity() -> None:
    assert return_on_equity(100, -200, 100) is None


def test_return_on_capital_employed() -> None:
    assert return_on_capital_employed(120, 200, 300, 100) == 20.00


def test_return_on_assets() -> None:
    assert return_on_assets(100, 1000) == 10.00


def test_debt_to_equity() -> None:
    assert debt_to_equity(100, 200, 300) == 0.20


def test_high_leverage_flag_non_financial() -> None:
    assert high_leverage_flag(6.0, "Industrials") is True


def test_high_leverage_flag_financial() -> None:
    assert high_leverage_flag(6.0, "Financials") is False


def test_interest_coverage_ratio() -> None:
    assert interest_coverage_ratio(200, 50, 50) == 5.0


def test_interest_coverage_zero_interest() -> None:
    assert interest_coverage_ratio(200, 50, 0) is None


def test_asset_turnover() -> None:
    assert asset_turnover(1000, 500) == 2.0


def test_free_cash_flow() -> None:
    assert free_cash_flow(120, -40) == 80.0


def test_capex_intensity() -> None:
    value, label = capex_intensity(-50, 1000)
    assert value == 5.0
    assert label == "Moderate"


def test_fcf_conversion_rate() -> None:
    assert fcf_conversion_rate(80, 100) == 80.0


def test_revenue_cagr_5yr() -> None:
    value, flag = revenue_cagr_5yr(100, 161.051)
    assert round(value, 2) == 10.00
    assert flag is None


def test_pat_cagr_5yr() -> None:
    value, flag = pat_cagr_5yr(100, 161.051)
    assert round(value, 2) == 10.00
    assert flag is None


def test_eps_cagr_5yr() -> None:
    value, flag = eps_cagr_5yr(100, 161.051)
    assert round(value, 2) == 10.00
    assert flag is None


def test_ratio_engine_integration_fields() -> None:
    engine = build_synthetic_engine()
    engine.records = [
        make_record(2019, 100.0, 10.0, 20.0),
        make_record(2020, 110.0, 11.0, 22.0),
        make_record(2021, 121.0, 12.1, 24.2),
        make_record(2022, 133.1, 13.31, 26.62),
        make_record(2023, 146.41, 14.64, 29.28),
        make_record(2024, 161.05, 16.11, 32.22),
    ]
    engine.company_history = engine._build_company_history()
    engine.calculate_ratios()

    latest = next(row for row in engine.ratio_results if row["year"] == "Mar 2024")

    assert latest["earnings_per_share"] == pytest.approx(1.611, abs=0.001)
    assert latest["book_value_per_share"] == 42.5
    assert latest["dividend_payout_ratio_pct"] == 12.5
    assert latest["total_debt_cr"] == 20.0
    assert latest["cash_from_operations_cr"] == 30.0
    assert latest["revenue_cagr_5yr"] == 10.0
    assert latest["pat_cagr_5yr"] == pytest.approx(10.01, abs=0.01)
    assert latest["eps_cagr_5yr"] == pytest.approx(10.01, abs=0.01)
    assert latest["composite_quality_score"] is not None
