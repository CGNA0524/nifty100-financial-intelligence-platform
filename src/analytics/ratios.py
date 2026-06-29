from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def net_profit_margin(
    net_profit: float,
    sales: float
) -> Optional[float]:
    """
    Net Profit Margin = (Net Profit / Sales) * 100
    """
    if sales == 0:
        return None

    return round((net_profit / sales) * 100, 2)


def operating_profit_margin(
    operating_profit: float,
    sales: float
) -> Optional[float]:
    """
    Operating Profit Margin = (Operating Profit / Sales) * 100
    """
    if sales == 0:
        return None

    return round((operating_profit / sales) * 100, 2)


def validate_opm(
    calculated_opm: Optional[float],
    source_opm: Optional[float],
    tolerance: float = 1.0
) -> bool:
    """
    Cross-check calculated OPM with source OPM.
    Log warning if difference > 1%
    """

    if calculated_opm is None or source_opm is None:
        return True

    difference = abs(calculated_opm - source_opm)

    if difference > tolerance:
        logger.warning(
            f"OPM mismatch: Calculated={calculated_opm}, "
            f"Source={source_opm}, Difference={difference:.2f}"
        )
        return False

    return True


def return_on_equity(
    net_profit: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:
    """
    ROE = Net Profit / (Equity + Reserves) * 100
    """

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round((net_profit / equity) * 100, 2)


def return_on_capital_employed(
    ebit: float,
    equity_capital: float,
    reserves: float,
    borrowings: float
) -> Optional[float]:
    """
    ROCE = EBIT / (Equity + Reserves + Borrowings) * 100
    """

    capital = equity_capital + reserves + borrowings

    if capital <= 0:
        return None

    return round((ebit / capital) * 100, 2)

def is_financial_company(broad_sector: str) -> bool:
    """
    Check whether the company belongs to Financials sector.
    """
    return broad_sector.strip().lower() == "financials"
def roce_status(roce: float, broad_sector: str) -> str:
    """
    Returns benchmark type for ROCE.
    """

    if is_financial_company(broad_sector):
        return "Sector Benchmark"

    if roce >= 15:
        return "Good"

    return "Needs Improvement"

def return_on_assets(
    net_profit: float,
    total_assets: float
) -> Optional[float]:
    """
    ROA = Net Profit / Total Assets * 100
    """

    if total_assets == 0:
        return None

    return round((net_profit / total_assets) * 100, 2)