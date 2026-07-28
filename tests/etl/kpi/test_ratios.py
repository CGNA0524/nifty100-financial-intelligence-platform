
from src.analytics.ratios import (
    asset_turnover,
    debt_to_equity,
    high_leverage_flag,
    icr_label,
    icr_warning_flag,
    interest_coverage_ratio,
    is_financial_company,
    net_debt,
    net_profit_margin,
    operating_profit_margin,
    return_on_assets,
    return_on_capital_employed,
    return_on_equity,
    roce_status,
    validate_opm,
)


def test_net_profit_margin():
    assert net_profit_margin(100, 1000) == 10.00


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(100, 0) is None


def test_operating_profit_margin():
    assert operating_profit_margin(250, 1000) == 25.00


def test_validate_opm_match():
    assert validate_opm(25.0, 25.4)


def test_validate_opm_mismatch():
    assert validate_opm(25.0, 30.0) is False


def test_return_on_equity():
    assert return_on_equity(100, 200, 300) == 20.00


def test_return_on_equity_negative_equity():
    assert return_on_equity(100, -200, 100) is None


def test_return_on_capital_employed():
    assert return_on_capital_employed(120, 200, 300, 100) == 20.00


def test_return_on_assets():
    assert return_on_assets(100, 1000) == 10.00


def test_financial_company():
    assert is_financial_company("Financials")


def test_non_financial_company():
    assert not is_financial_company("IT")


def test_roce_financial():
    assert roce_status(8, "Financials") == "Sector Benchmark"


def test_return_on_assets_zero_assets():
    assert return_on_assets(100, 0) is None


# -------------------------
# Day 09 Tests
# -------------------------


def test_debt_to_equity():
    assert debt_to_equity(100, 200, 300) == 0.20


def test_debt_to_equity_debt_free():
    assert debt_to_equity(0, 200, 300) == 0.0


def test_high_leverage_flag():
    assert high_leverage_flag(6.0, "IT") is True


def test_high_leverage_financial():
    assert high_leverage_flag(10.0, "Financials") is False


def test_interest_coverage_ratio():
    assert interest_coverage_ratio(200, 50, 50) == 5.0


def test_interest_coverage_zero_interest():
    assert interest_coverage_ratio(200, 50, 0) is None


def test_icr_label():
    assert icr_label(0) == "Debt Free"


def test_icr_warning():
    assert icr_warning_flag(1.2) is True


def test_net_debt():
    assert net_debt(500, 100) == 400


def test_asset_turnover():
    assert asset_turnover(1000, 500) == 2.0


def test_asset_turnover_zero_assets():
    assert asset_turnover(1000, 0) is None
