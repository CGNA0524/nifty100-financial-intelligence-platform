import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def net_profit_margin(net_profit: float, sales: float) -> float | None:
    """
    Net Profit Margin = (Net Profit / Sales) * 100
    """
    if sales == 0:
        return None

    return round((net_profit / sales) * 100, 2)


def operating_profit_margin(operating_profit: float, sales: float) -> float | None:
    """
    Operating Profit Margin = (Operating Profit / Sales) * 100
    """
    if sales == 0:
        return None

    return round((operating_profit / sales) * 100, 2)


def validate_opm(
    calculated_opm: float | None, source_opm: float | None, tolerance: float = 1.0
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
    net_profit: float, equity_capital: float, reserves: float
) -> float | None:
    """
    ROE = Net Profit / (Equity + Reserves) * 100
    """

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round((net_profit / equity) * 100, 2)


def return_on_capital_employed(
    ebit: float, equity_capital: float, reserves: float, borrowings: float
) -> float | None:
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
    if not broad_sector:
        return False

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


def return_on_assets(net_profit: float, total_assets: float) -> float | None:
    """
    ROA = Net Profit / Total Assets * 100
    """

    if total_assets == 0:
        return None

    return round((net_profit / total_assets) * 100, 2)


def debt_to_equity(
    borrowings: float, equity_capital: float, reserves: float
) -> float | None:
    """
    Debt to Equity Ratio
    """

    if borrowings == 0:
        return 0.0

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round(borrowings / equity, 2)


def high_leverage_flag(debt_equity: float | None, broad_sector: str) -> bool:
    """
    Returns True if D/E > 5 and company is not Financials.
    """

    if debt_equity is None:
        return False

    if is_financial_company(broad_sector):
        return False

    return debt_equity > 5


def interest_coverage_ratio(
    operating_profit: float, other_income: float, interest: float
) -> float | None:
    """
    Interest Coverage Ratio (ICR)

    Formula:
    (Operating Profit + Other Income) / Interest
    """

    if interest == 0:
        return None

    return round((operating_profit + other_income) / interest, 2)


def icr_label(interest: float) -> str:
    """
    Return label for Interest Coverage Ratio.
    """

    if interest == 0:
        return "Debt Free"

    return "Has Debt"


def icr_warning_flag(icr: float | None) -> bool:
    """
    Warning if Interest Coverage Ratio is below 1.5
    """

    if icr is None:
        return False

    return icr < 1.5


def net_debt(borrowings: float, investments: float) -> float:
    """
    Net Debt

    Formula:
    Borrowings - Investments
    """

    return round(borrowings - investments, 2)


def asset_turnover(sales: float, total_assets: float) -> float | None:
    """
    Asset Turnover

    Formula:
    Sales / Total Assets
    """

    if total_assets == 0:
        return None

    return round(sales / total_assets, 2)


def free_cash_flow(operating_activity: float, investing_activity: float) -> float:
    """
    Free Cash Flow (FCF)

    Formula:
    CFO + Investing Activity

    Investing Activity is generally negative.
    Negative FCF is allowed.
    """

    return round(operating_activity + investing_activity, 2)


def cfo_quality_score(avg_cfo: float, avg_pat: float) -> tuple[float, str] | None:
    """
    CFO Quality Score

    Formula:
    Average CFO / Average PAT (5-year average)

    >1.0  -> High Quality
    0.5-1 -> Moderate
    <0.5  -> Accrual Risk

    Return None if PAT is zero.
    """

    if avg_pat == 0:
        return None

    score = round(avg_cfo / avg_pat, 2)

    if score > 1.0:
        label = "High Quality"
    elif score >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"

    return score, label


def capex_intensity(
    investing_activity: float, sales: float
) -> tuple[float, str] | None:
    """
    CapEx Intensity

    Formula:
    abs(Investing Activity) / Sales * 100

    <3%  -> Asset Light
    3-8% -> Moderate
    >8%  -> Capital Intensive
    """

    if sales == 0:
        return None

    intensity = round((abs(investing_activity) / sales) * 100, 2)

    if intensity < 3:
        label = "Asset Light"
    elif intensity <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return intensity, label


def fcf_conversion_rate(
    free_cash_flow: float, operating_profit: float
) -> float | None:
    """
    FCF Conversion Rate

    Formula:
    FCF / Operating Profit * 100

    Return None if Operating Profit is zero.
    """

    if operating_profit == 0:
        return None

    return round((free_cash_flow / operating_profit) * 100, 2)


def capital_allocation_pattern(
    operating_activity: float,
    investing_activity: float,
    financing_activity: float,
    cfo_pat_ratio: float | None = None,
) -> str:
    """
    Capital Allocation Pattern Classifier

    CFO  = Operating Activity
    CFI  = Investing Activity
    CFF  = Financing Activity
    """

    cfo = "+" if operating_activity >= 0 else "-"
    cfi = "+" if investing_activity >= 0 else "-"
    cff = "+" if financing_activity >= 0 else "-"

    pattern = (cfo, cfi, cff)

    if pattern == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1.0:
            return "Shareholder Returns"
        return "Reinvestor"

    elif pattern == ("+", "+", "-"):
        return "Liquidating Assets"

    elif pattern == ("-", "+", "+"):
        return "Distress Signal"

    elif pattern == ("-", "-", "+"):
        return "Growth Funded by Debt"

    elif pattern == ("+", "+", "+"):
        return "Cash Accumulator"

    elif pattern == ("-", "-", "-"):
        return "Pre-Revenue"

    elif pattern == ("+", "-", "+"):
        return "Mixed"

    return "Unknown"
