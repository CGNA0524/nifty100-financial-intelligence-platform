from typing import Optional, Tuple


def calculate_cagr(
    start_value: float,
    end_value: float,
    years: int
) -> Tuple[Optional[float], Optional[str]]:
    """
    CAGR Formula:
    ((End / Start) ** (1 / Years) - 1) * 100
    """

    if years <= 0:
        return None, "INSUFFICIENT"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value > 0 and end_value > 0:
        cagr = ((end_value / start_value) ** (1 / years) - 1) * 100
        return round(cagr, 2), None

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    return None, "INSUFFICIENT"

def revenue_cagr(
    start_revenue: float,
    end_revenue: float,
    years: int
) -> Tuple[Optional[float], Optional[str]]:
    """
    Revenue CAGR
    """
    return calculate_cagr(start_revenue, end_revenue, years)

def revenue_cagr_3yr(start_revenue: float, end_revenue: float) -> Tuple[Optional[float], Optional[str]]:
    """
    Revenue CAGR - 3 Years
    """
    return calculate_cagr(start_revenue, end_revenue, 3)


def revenue_cagr_5yr(start_revenue: float, end_revenue: float) -> Tuple[Optional[float], Optional[str]]:
    """
    Revenue CAGR - 5 Years
    """
    return calculate_cagr(start_revenue, end_revenue, 5)


def revenue_cagr_10yr(start_revenue: float, end_revenue: float) -> Tuple[Optional[float], Optional[str]]:
    """
    Revenue CAGR - 10 Years
    """
    return calculate_cagr(start_revenue, end_revenue, 10)

def pat_cagr_3yr(start_pat: float, end_pat: float) -> Tuple[Optional[float], Optional[str]]:
    """
    PAT CAGR - 3 Years
    """
    return calculate_cagr(start_pat, end_pat, 3)


def pat_cagr_5yr(start_pat: float, end_pat: float) -> Tuple[Optional[float], Optional[str]]:
    """
    PAT CAGR - 5 Years
    """
    return calculate_cagr(start_pat, end_pat, 5)


def pat_cagr_10yr(start_pat: float, end_pat: float) -> Tuple[Optional[float], Optional[str]]:
    """
    PAT CAGR - 10 Years
    """
    return calculate_cagr(start_pat, end_pat, 10)

def pat_cagr(
    start_pat: float,
    end_pat: float,
    years: int
) -> Tuple[Optional[float], Optional[str]]:
    """
    PAT CAGR
    """
    return calculate_cagr(start_pat, end_pat, years)

def eps_cagr_3yr(start_eps: float, end_eps: float) -> Tuple[Optional[float], Optional[str]]:
    """
    EPS CAGR - 3 Years
    """
    return calculate_cagr(start_eps, end_eps, 3)


def eps_cagr_5yr(start_eps: float, end_eps: float) -> Tuple[Optional[float], Optional[str]]:
    """
    EPS CAGR - 5 Years
    """
    return calculate_cagr(start_eps, end_eps, 5)


def eps_cagr_10yr(start_eps: float, end_eps: float) -> Tuple[Optional[float], Optional[str]]:
    """
    EPS CAGR - 10 Years
    """
    return calculate_cagr(start_eps, end_eps, 10)


def eps_cagr(
    start_eps: float,
    end_eps: float,
    years: int
) -> Tuple[Optional[float], Optional[str]]:
    """
    EPS CAGR
    """
    return calculate_cagr(start_eps, end_eps, years)


def free_cash_flow_cagr(
    start_fcf: float,
    end_fcf: float,
    years: int
) -> Tuple[Optional[float], Optional[str]]:
    """
    Free Cash Flow CAGR
    """
    return calculate_cagr(start_fcf, end_fcf, years)