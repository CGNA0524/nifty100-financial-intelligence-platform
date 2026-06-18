import sys
import os

sys.path.append(os.path.abspath("src/etl"))

from normaliser import normalize_ticker, normalize_year


# =========================
# normalize_ticker Tests
# =========================

def test_ticker_01():
    assert normalize_ticker("tcs") == "TCS"

def test_ticker_02():
    assert normalize_ticker(" infy ") == "INFY"

def test_ticker_03():
    assert normalize_ticker("hdfcbank") == "HDFCBANK"

def test_ticker_04():
    assert normalize_ticker("reliance") == "RELIANCE"

def test_ticker_05():
    assert normalize_ticker("ITC") == "ITC"

def test_ticker_06():
    assert normalize_ticker(" sbin ") == "SBIN"

def test_ticker_07():
    assert normalize_ticker("lt") == "LT"

def test_ticker_08():
    assert normalize_ticker("asianpaint") == "ASIANPAINT"

def test_ticker_09():
    assert normalize_ticker("nestleind") == "NESTLEIND"

def test_ticker_10():
    assert normalize_ticker("techm") == "TECHM"

def test_ticker_11():
    assert normalize_ticker("tatamotors") == "TATAMOTORS"

def test_ticker_12():
    assert normalize_ticker("sunpharma") == "SUNPHARMA"

def test_ticker_13():
    assert normalize_ticker("ultracemco") == "ULTRACEMCO"

def test_ticker_14():
    assert normalize_ticker("wipro") == "WIPRO"

def test_ticker_15():
    assert normalize_ticker("axisbank") == "AXISBANK"


# =========================
# normalize_year Tests
# =========================

def test_year_01():
    assert normalize_year("Mar-24") == "2024-03"

def test_year_02():
    assert normalize_year("Mar-23") == "2023-03"

def test_year_03():
    assert normalize_year("Mar-22") == "2022-03"

def test_year_04():
    assert normalize_year("Jun-24") == "2024-06"

def test_year_05():
    assert normalize_year("Sep-24") == "2024-09"

def test_year_06():
    assert normalize_year("Dec-24") == "2024-12"

def test_year_07():
    assert normalize_year("Jan-24") == "2024-01"

def test_year_08():
    assert normalize_year("Feb-24") == "2024-02"

def test_year_09():
    assert normalize_year("Apr-24") == "2024-04"

def test_year_10():
    assert normalize_year("May-24") == "2024-05"

def test_year_11():
    assert normalize_year("Jul-24") == "2024-07"

def test_year_12():
    assert normalize_year("Aug-24") == "2024-08"

def test_year_13():
    assert normalize_year("Oct-24") == "2024-10"

def test_year_14():
    assert normalize_year("Nov-24") == "2024-11"

def test_year_15():
    assert normalize_year("Dec-23") == "2023-12"

def test_year_16():
    assert normalize_year("Sep-23") == "2023-09"

def test_year_17():
    assert normalize_year("Jun-23") == "2023-06"

def test_year_18():
    assert normalize_year("Mar-21") == "2021-03"

def test_year_19():
    assert normalize_year("Mar-20") == "2020-03"

def test_year_20():
    assert normalize_year("Mar-19") == "2019-03"