import pytest

from src.analytics.ratios import (
    is_financial_company,
    net_profit_margin,
    operating_profit_margin,
    roce_status,
    validate_opm,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
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
