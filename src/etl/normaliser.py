import re


def normalize_ticker(ticker):
    """
    Convert company ticker to standard format.
    Example:
    ' tcs ' -> 'TCS'
    """
    if ticker is None:
        return None

    return str(ticker).strip().upper()


def normalize_year(year):
    """
    Convert year values like:
    Mar-24 -> 2024-03
    Mar-23 -> 2023-03
    """

    if year is None:
        return None

    year = str(year).strip()

    match = re.match(r"([A-Za-z]{3})-(\d{2})", year)

    if not match:
        return year

    month = match.group(1)
    yr = int(match.group(2))

    full_year = 2000 + yr

    month_map = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12"
    }

    return f"{full_year}-{month_map.get(month, '01')}"