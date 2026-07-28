"""Ratio engine for merging financial statements and storing KPI outputs."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

from src.analytics.cagr import (
    eps_cagr_5yr,
    pat_cagr_5yr,
    revenue_cagr_5yr,
)
from src.analytics.ratios import (
    asset_turnover,
    capex_intensity,
    cfo_quality_score,
    debt_to_equity,
    fcf_conversion_rate,
    free_cash_flow,
    interest_coverage_ratio,
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
)

logger = logging.getLogger(__name__)


class RatioEngine:
    """Load financial statements, calculate ratios, and persist results."""

    PROFIT_TABLE = "profitandloss"
    BALANCE_TABLE = "balancesheet"
    CASHFLOW_TABLE = "cashflow"
    COMPANY_TABLE = "companies"
    RATIO_TABLE = "financial_ratios"

    REQUIRED_RATIO_COLUMNS = (
        "company_id",
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_cr",
        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",
        "cash_from_operations_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score",
    )

    EXPECTED_RATIO_COLUMN_TYPES = {
        "company_id": ("TEXT",),
        "year": ("TEXT",),
        "net_profit_margin_pct": ("REAL",),
        "operating_profit_margin_pct": ("REAL",),
        "return_on_equity_pct": ("REAL",),
        "debt_to_equity": ("REAL",),
        "interest_coverage": ("REAL",),
        "asset_turnover": ("REAL",),
        "free_cash_flow_cr": ("REAL",),
        "capex_cr": ("REAL",),
        "earnings_per_share": ("REAL",),
        "book_value_per_share": ("REAL",),
        "dividend_payout_ratio_pct": ("REAL",),
        "total_debt_cr": ("REAL",),
        "cash_from_operations_cr": ("REAL",),
        "revenue_cagr_5yr": ("REAL",),
        "pat_cagr_5yr": ("REAL",),
        "eps_cagr_5yr": ("REAL",),
        "composite_quality_score": ("REAL",),
    }

    def __init__(self, db_path: str | None = None) -> None:
        """Initialize the SQLite connection and in-memory data containers."""

        base_path = Path(__file__).resolve().parents[2]
        resolved_db_path = (
            Path(db_path) if db_path is not None else base_path / "db" / "nifty100.db"
        )

        self.db_path = str(resolved_db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.pnl: list[sqlite3.Row] = []
        self.balance: list[sqlite3.Row] = []
        self.cashflow: list[sqlite3.Row] = []
        self.companies: list[sqlite3.Row] = []
        self.records: list[dict[str, Any]] = []
        self.ratio_results: list[dict[str, Any]] = []
        self.record_lookup: dict[tuple[Any, Any], dict[str, Any]] = {}
        self.company_lookup: dict[Any, sqlite3.Row] = {}
        self.company_history: dict[Any, list[dict[str, Any]]] = {}

    def fetch_table(self, table_name: str) -> list[sqlite3.Row]:
        """Fetch all rows from a table using the current SQLite connection."""

        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def load_data(self) -> None:
        """Load the source financial statement tables into memory."""

        try:
            # Load each source statement table into SQLite Row collections.
            self.pnl = self.fetch_table(self.PROFIT_TABLE)
            self.balance = self.fetch_table(self.BALANCE_TABLE)
            self.cashflow = self.fetch_table(self.CASHFLOW_TABLE)
            self.companies = self.fetch_table(self.COMPANY_TABLE)
            self.company_lookup = {
                row["id"]: row for row in self.companies if row["id"] is not None
            }
        except sqlite3.Error:
            logger.exception("Failed to load source tables")
            raise

        print(f"Profit & Loss Rows : {len(self.pnl)}")
        print(f"Balance Sheet Rows : {len(self.balance)}")
        print(f"Cash Flow Rows     : {len(self.cashflow)}")
        print(f"Rows Loaded : {len(self.pnl) + len(self.balance) + len(self.cashflow)}")

    def build_lookup(
        self, rows: list[sqlite3.Row]
    ) -> dict[tuple[Any, Any], sqlite3.Row]:
        """Create a lookup keyed by company_id and year."""

        lookup: dict[tuple[Any, Any], sqlite3.Row] = {}

        for row in rows:
            key = (row["company_id"], row["year"])
            lookup[key] = row

        return lookup

    def prepare_data(self) -> None:
        """Merge the three statements using the common (company_id, year) key."""

        # Build fast lookups and keep only records present in all three tables.
        pnl_lookup = self.build_lookup(self.pnl)
        balance_lookup = self.build_lookup(self.balance)
        cashflow_lookup = self.build_lookup(self.cashflow)

        common_keys = set(pnl_lookup) & set(balance_lookup) & set(cashflow_lookup)
        self.records = []

        for company_id, year in sorted(common_keys):
            company_row = self.company_lookup.get(company_id)
            record = {
                "company_id": company_id,
                "year": year,
                "pnl": pnl_lookup[(company_id, year)],
                "balance": balance_lookup[(company_id, year)],
                "cashflow": cashflow_lookup[(company_id, year)],
                "company": company_row,
            }
            self.records.append(record)
            self.record_lookup[(company_id, year)] = record

        self.company_history = self._build_company_history()

        print(f"Merged Records : {len(self.records)}")
        print(f"Rows Merged : {len(self.records)}")

    def calculate_ratios(self) -> None:
        """Calculate all requested ratios for each merged record."""

        self.ratio_results = []

        for record in self.records:
            # Read source values defensively so None never reaches the formulas.
            pnl = record["pnl"]
            bs = record["balance"]
            cf = record["cashflow"]
            company = record.get("company")

            sales = self._safe_number(pnl["sales"])
            net_profit = self._safe_number(pnl["net_profit"])
            operating_profit = self._safe_number(pnl["operating_profit"])
            other_income = self._safe_number(pnl["other_income"])
            interest = self._safe_number(pnl["interest"])
            eps = self._safe_number(pnl["eps"])
            dividend_payout_ratio = self._safe_number(pnl["dividend_payout"])

            equity_capital = self._safe_number(bs["equity_capital"])
            reserves = self._safe_number(bs["reserves"])
            borrowings = self._safe_number(bs["borrowings"])
            total_assets = self._safe_number(bs["total_assets"])

            operating_activity = self._safe_number(cf["operating_activity"])
            investing_activity = self._safe_number(cf["investing_activity"])

            earnings_per_share = eps
            book_value_per_share = self._get_book_value_per_share(company)
            total_debt_cr = borrowings
            cash_from_operations_cr = operating_activity

            capex_value = capex_intensity(investing_activity, sales)
            capex_cr = capex_value[0] if capex_value is not None else None

            fcf = free_cash_flow(operating_activity, investing_activity)
            fcf_conversion = fcf_conversion_rate(fcf, operating_profit)

            net_profit_margin_pct = net_profit_margin(net_profit, sales)
            operating_profit_margin_pct = operating_profit_margin(
                operating_profit,
                sales,
            )
            return_on_equity_pct = return_on_equity(
                net_profit,
                equity_capital,
                reserves,
            )
            debt_to_equity_value = debt_to_equity(
                borrowings,
                equity_capital,
                reserves,
            )
            interest_coverage_value = interest_coverage_ratio(
                operating_profit,
                other_income,
                interest,
            )
            asset_turnover_value = asset_turnover(sales, total_assets)

            revenue_cagr_value = self._get_cagr_value(
                record,
                "sales",
                revenue_cagr_5yr,
            )
            pat_cagr_value = self._get_cagr_value(
                record,
                "net_profit",
                pat_cagr_5yr,
            )
            eps_cagr_value = self._get_cagr_value(
                record,
                "eps",
                eps_cagr_5yr,
            )
            composite_quality_score = self._calculate_composite_quality_score(
                company_id=record["company_id"],
                return_on_equity_pct=return_on_equity_pct,
                operating_profit_margin_pct=operating_profit_margin_pct,
                debt_to_equity_value=debt_to_equity_value,
                fcf_conversion_rate_pct=fcf_conversion,
                revenue_cagr_5yr_value=revenue_cagr_value,
                pat_cagr_5yr_value=pat_cagr_value,
                eps_cagr_5yr_value=eps_cagr_value,
            )

            result = {
                "company_id": record["company_id"],
                "year": record["year"],
                "net_profit_margin_pct": net_profit_margin_pct,
                "operating_profit_margin_pct": operating_profit_margin_pct,
                "return_on_equity_pct": return_on_equity_pct,
                "debt_to_equity": debt_to_equity_value,
                "interest_coverage": interest_coverage_value,
                "asset_turnover": asset_turnover_value,
                "free_cash_flow_cr": fcf,
                "capex_cr": capex_cr,
                "earnings_per_share": earnings_per_share,
                "book_value_per_share": book_value_per_share,
                "dividend_payout_ratio_pct": dividend_payout_ratio,
                "total_debt_cr": total_debt_cr,
                "cash_from_operations_cr": cash_from_operations_cr,
                "revenue_cagr_5yr": revenue_cagr_value,
                "pat_cagr_5yr": pat_cagr_value,
                "eps_cagr_5yr": eps_cagr_value,
                "composite_quality_score": composite_quality_score,
                "fcf_conversion_rate_pct": fcf_conversion,
            }

            self.ratio_results.append(result)

        print(f"Calculated KPIs : {len(self.ratio_results)}")
        print(f"Rows Calculated : {len(self.ratio_results)}")

    def save_to_database(self) -> None:
        """Replace financial_ratios rows with the current ratio results."""

        inserted_rows = 0
        insert_rows: list[tuple[Any, ...]] = []

        try:
            # Validate the target table and schema before mutating data.
            if not self._table_exists(self.RATIO_TABLE):
                logger.error("Table %s does not exist", self.RATIO_TABLE)
                return

            existing_columns = self._get_table_columns(self.RATIO_TABLE)
            if not self._required_columns_exist(existing_columns):
                logger.error(
                    "Table %s is missing required columns",
                    self.RATIO_TABLE,
                )
                return

            if not self._validate_ratio_table_schema():
                logger.error("Table %s failed schema validation", self.RATIO_TABLE)
                return

            self.cursor.execute(f"SELECT COUNT(*) FROM {self.RATIO_TABLE}")
            existing_row = self.cursor.fetchone()
            rows_before_delete = existing_row[0] if existing_row is not None else 0

            # Replace the table contents inside a single transaction.
            with self.conn:
                self.cursor.execute(f"DELETE FROM {self.RATIO_TABLE}")
                print(f"Deleted {rows_before_delete} rows from {self.RATIO_TABLE}")

                insert_rows = self._build_insert_rows()
                if insert_rows:
                    insert_query = (
                        f"INSERT INTO {self.RATIO_TABLE} ("
                        "company_id, year, net_profit_margin_pct, "
                        "operating_profit_margin_pct, return_on_equity_pct, "
                        "debt_to_equity, interest_coverage, asset_turnover, "
                        "free_cash_flow_cr, capex_cr, earnings_per_share, "
                        "book_value_per_share, dividend_payout_ratio_pct, "
                        "total_debt_cr, cash_from_operations_cr, revenue_cagr_5yr, "
                        "pat_cagr_5yr, eps_cagr_5yr, composite_quality_score"
                        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    )
                    self.cursor.executemany(insert_query, insert_rows)
                    inserted_rows = len(insert_rows)

        except sqlite3.Error:
            self.conn.rollback()
            logger.exception("Database write failed")
            raise

        print("Database Commit Successful")
        print(f"Saved {inserted_rows} rows into financial_ratios")
        print(f"Rows Inserted : {inserted_rows}")
        self.verify_database(inserted_rows)

    def close(self) -> None:
        """Close the SQLite connection safely."""

        try:
            # Close only when the connection is still available.
            if self.conn:
                self.conn.close()
        except sqlite3.Error:
            logger.exception("Failed to close database connection")

    def _table_exists(self, table_name: str) -> bool:
        """Return True when the target table exists in SQLite."""

        query = "SELECT 1 FROM sqlite_master WHERE type = ? AND name = ?"
        self.cursor.execute(query, ("table", table_name))
        return self.cursor.fetchone() is not None

    def _get_table_columns(self, table_name: str) -> set[str]:
        """Return the column names for a SQLite table."""

        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return {row["name"] for row in self.cursor.fetchall()}

    def _required_columns_exist(self, columns: set[str]) -> bool:
        """Check whether all required output columns exist."""

        return set(self.REQUIRED_RATIO_COLUMNS).issubset(columns)

    def _build_insert_rows(self) -> list[tuple[Any, ...]]:
        """Prepare validated rows for batch insertion into SQLite."""

        insert_rows: list[tuple[Any, ...]] = []

        for row in self.ratio_results:
            company_id = row.get("company_id")
            year = row.get("year")

            if company_id is None or year is None:
                continue

            insert_rows.append(
                (
                    company_id,
                    year,
                    row.get("net_profit_margin_pct"),
                    row.get("operating_profit_margin_pct"),
                    row.get("return_on_equity_pct"),
                    row.get("debt_to_equity"),
                    row.get("interest_coverage"),
                    row.get("asset_turnover"),
                    row.get("free_cash_flow_cr"),
                    row.get("capex_cr"),
                    row.get("earnings_per_share"),
                    row.get("book_value_per_share"),
                    row.get("dividend_payout_ratio_pct"),
                    row.get("total_debt_cr"),
                    row.get("cash_from_operations_cr"),
                    row.get("revenue_cagr_5yr"),
                    row.get("pat_cagr_5yr"),
                    row.get("eps_cagr_5yr"),
                    row.get("composite_quality_score"),
                )
            )

        return insert_rows

    def _validate_ratio_table_schema(self) -> bool:
        """Validate declared column types and primary key metadata in SQLite."""

        self.cursor.execute(f"PRAGMA table_info({self.RATIO_TABLE})")
        schema_rows = self.cursor.fetchall()

        if not schema_rows:
            return False

        schema_types = {row["name"]: (row["type"] or "").upper() for row in schema_rows}
        primary_key_columns = [row["name"] for row in schema_rows if row["pk"]]

        if "id" not in primary_key_columns:
            logger.error("Primary key validation failed for %s", self.RATIO_TABLE)
            return False

        for column_name, expected_types in self.EXPECTED_RATIO_COLUMN_TYPES.items():
            actual_type = schema_types.get(column_name)
            if actual_type is None:
                logger.error("Missing column %s in %s", column_name, self.RATIO_TABLE)
                return False

            if actual_type not in expected_types:
                logger.error(
                    "Column %s has type %s, expected %s",
                    column_name,
                    actual_type,
                    "/".join(expected_types),
                )
                return False

        return True

    def _safe_number(self, value: Any, default: Any = 0.0) -> Any:
        """Return a safe numeric fallback for None values."""

        if value is None:
            return default

        return value

    def _get_book_value_per_share(self, company: sqlite3.Row | None) -> Any:
        """Return book value per share from the companies table when available."""

        if company is None or "book_value" not in company.keys():
            return None

        return self._safe_number(company["book_value"], default=None)

    def verify_database(self, expected_rows: int) -> None:
        """Print the row-count verification summary for the target table."""

        self.cursor.execute(f"SELECT COUNT(*) FROM {self.RATIO_TABLE}")
        row = self.cursor.fetchone()
        actual_rows = row[0] if row is not None else 0
        status = "PASS" if actual_rows == expected_rows else "FAIL"

        print(f"Expected Rows : {expected_rows}")
        print(f"Actual Rows : {actual_rows}")
        print(status)

    def spot_check(self, company_id: Any, year: Any) -> None:
        """Print every KPI stored for one company-year record."""

        for row in self.ratio_results:
            if row.get("company_id") == company_id and row.get("year") == year:
                for key, value in row.items():
                    print(f"{key} : {value}")
                return

        print(f"No KPI row found for {company_id} / {year}")

    def print_sample_companies(self, limit: int = 3) -> None:
        """Print compact KPI summaries for a few calculated company-year rows."""

        for row in self.ratio_results[:limit]:
            print(
                "Sample KPI - "
                f"company_id={row.get('company_id')}, "
                f"year={row.get('year')}, "
                f"ROE={row.get('return_on_equity_pct')}, "
                f"Revenue CAGR={row.get('revenue_cagr_5yr')}, "
                f"EPS CAGR={row.get('eps_cagr_5yr')}, "
                f"Free Cash Flow={row.get('free_cash_flow_cr')}, "
                f"Composite Score={row.get('composite_quality_score')}"
            )

    def validation_sql_queries(self) -> dict[str, str]:
        """Return SQL snippets for manual table validation."""

        return {
            "total_row_count": f"SELECT COUNT(*) AS total_rows FROM {self.RATIO_TABLE};",
            "null_kpi_count": f"""
                SELECT
                    SUM(CASE WHEN net_profit_margin_pct IS NULL THEN 1 ELSE 0 END) AS net_profit_margin_nulls,
                    SUM(CASE WHEN operating_profit_margin_pct IS NULL THEN 1 ELSE 0 END) AS operating_profit_margin_nulls,
                    SUM(CASE WHEN return_on_equity_pct IS NULL THEN 1 ELSE 0 END) AS roe_nulls,
                    SUM(CASE WHEN debt_to_equity IS NULL THEN 1 ELSE 0 END) AS debt_to_equity_nulls,
                    SUM(CASE WHEN interest_coverage IS NULL THEN 1 ELSE 0 END) AS interest_coverage_nulls,
                    SUM(CASE WHEN asset_turnover IS NULL THEN 1 ELSE 0 END) AS asset_turnover_nulls,
                    SUM(CASE WHEN free_cash_flow_cr IS NULL THEN 1 ELSE 0 END) AS fcf_nulls,
                    SUM(CASE WHEN capex_cr IS NULL THEN 1 ELSE 0 END) AS capex_nulls,
                    SUM(CASE WHEN earnings_per_share IS NULL THEN 1 ELSE 0 END) AS eps_nulls,
                    SUM(CASE WHEN book_value_per_share IS NULL THEN 1 ELSE 0 END) AS book_value_per_share_nulls,
                    SUM(CASE WHEN dividend_payout_ratio_pct IS NULL THEN 1 ELSE 0 END) AS dividend_payout_ratio_nulls,
                    SUM(CASE WHEN total_debt_cr IS NULL THEN 1 ELSE 0 END) AS total_debt_nulls,
                    SUM(CASE WHEN cash_from_operations_cr IS NULL THEN 1 ELSE 0 END) AS cfo_nulls,
                    SUM(CASE WHEN revenue_cagr_5yr IS NULL THEN 1 ELSE 0 END) AS revenue_cagr_nulls,
                    SUM(CASE WHEN pat_cagr_5yr IS NULL THEN 1 ELSE 0 END) AS pat_cagr_nulls,
                    SUM(CASE WHEN eps_cagr_5yr IS NULL THEN 1 ELSE 0 END) AS eps_cagr_nulls,
                    SUM(CASE WHEN composite_quality_score IS NULL THEN 1 ELSE 0 END) AS composite_score_nulls
                FROM {self.RATIO_TABLE};
            """,
            "duplicate_company_year": f"""
                SELECT company_id, year, COUNT(*) AS row_count
                FROM {self.RATIO_TABLE}
                GROUP BY company_id, year
                HAVING COUNT(*) > 1;
            """,
            "top_10_roe": f"""
                SELECT company_id, year, return_on_equity_pct
                FROM {self.RATIO_TABLE}
                WHERE return_on_equity_pct IS NOT NULL
                ORDER BY return_on_equity_pct DESC
                LIMIT 10;
            """,
            "top_10_revenue_cagr": f"""
                SELECT company_id, year, revenue_cagr_5yr
                FROM {self.RATIO_TABLE}
                WHERE revenue_cagr_5yr IS NOT NULL
                ORDER BY revenue_cagr_5yr DESC
                LIMIT 10;
            """,
            "bottom_10_revenue_cagr": f"""
                SELECT company_id, year, revenue_cagr_5yr
                FROM {self.RATIO_TABLE}
                WHERE revenue_cagr_5yr IS NOT NULL
                ORDER BY revenue_cagr_5yr ASC
                LIMIT 10;
            """,
            "companies_missing_cagr": f"""
                SELECT company_id, year
                FROM {self.RATIO_TABLE}
                WHERE revenue_cagr_5yr IS NULL
                   OR pat_cagr_5yr IS NULL
                   OR eps_cagr_5yr IS NULL;
            """,
            "companies_with_negative_equity": f"""
                SELECT company_id, year
                FROM {self.RATIO_TABLE}
                WHERE return_on_equity_pct IS NULL
                   OR debt_to_equity IS NULL;
            """,
            "companies_with_negative_fcf": f"""
                SELECT company_id, year, free_cash_flow_cr
                FROM {self.RATIO_TABLE}
                WHERE free_cash_flow_cr < 0;
            """,
        }

    def _build_company_history(self) -> dict[Any, list[dict[str, Any]]]:
        """Group merged records by company and sort them by year."""

        history: dict[Any, list[dict[str, Any]]] = {}

        for record in self.records:
            company_id = record["company_id"]
            history.setdefault(company_id, []).append(record)

        for items in history.values():
            items.sort(key=lambda item: self._year_sort_key(item["year"]) or -1)

        return history

    def _get_historical_record(
        self,
        company_id: Any,
        year: Any,
        years_back: int,
    ) -> dict[str, Any] | None:
        """Fetch a historical merged record for the same company."""

        current_year = self._year_sort_key(year)
        if current_year is None:
            return None

        target_year = current_year - years_back

        for record in self.company_history.get(company_id, []):
            if self._year_sort_key(record["year"]) == target_year:
                return record

        return None

    def _year_sort_key(self, year_value: Any) -> int | None:
        """Return a sortable numeric year from the stored year value."""

        if year_value is None:
            return None

        year_text = str(year_value)
        digits_only = "".join(
            character for character in year_text if character.isdigit()
        )

        if len(digits_only) >= 4:
            return int(digits_only[:4])

        if digits_only.isdigit():
            return int(digits_only)

        return None

    def _get_cagr_value(
        self,
        record: dict[str, Any],
        value_key: str,
        cagr_function: Any,
    ) -> Any:
        """Calculate a 5-year CAGR using the historical merged record."""

        historical_record = self._get_historical_record(
            record["company_id"],
            record["year"],
            5,
        )

        if historical_record is None:
            return None

        historical_row = historical_record["pnl"]
        current_row = record["pnl"]
        start_value = self._safe_number(historical_row[value_key])
        end_value = self._safe_number(current_row[value_key])
        cagr_value, _ = cagr_function(start_value, end_value)
        return cagr_value

    def _calculate_composite_quality_score(
        self,
        company_id: Any,
        return_on_equity_pct: Any,
        operating_profit_margin_pct: Any,
        debt_to_equity_value: Any,
        fcf_conversion_rate_pct: Any,
        revenue_cagr_5yr_value: Any,
        pat_cagr_5yr_value: Any,
        eps_cagr_5yr_value: Any,
    ) -> Any:
        """Blend profitability, growth, cash conversion, leverage and CFO quality.

        The score is the average of available component scores normalized to a
        0-100 scale. This keeps the metric comparable across companies while
        avoiding a single-factor result.
        """

        components: list[float] = []

        roe_score = self._scale_between(return_on_equity_pct, -10.0, 30.0)
        if roe_score is not None:
            components.append(roe_score)

        opm_score = self._scale_between(operating_profit_margin_pct, 0.0, 25.0)
        if opm_score is not None:
            components.append(opm_score)

        growth_values = [
            value
            for value in (
                revenue_cagr_5yr_value,
                pat_cagr_5yr_value,
                eps_cagr_5yr_value,
            )
            if value is not None
        ]
        if growth_values:
            growth_average = sum(growth_values) / len(growth_values)
            growth_score = self._scale_between(growth_average, -20.0, 25.0)
            if growth_score is not None:
                components.append(growth_score)

        cash_score = self._scale_between(fcf_conversion_rate_pct, 0.0, 150.0)
        if cash_score is not None:
            components.append(cash_score)

        if debt_to_equity_value is not None:
            leverage_score = max(0.0, 100.0 - (float(debt_to_equity_value) * 15.0))
            components.append(leverage_score)

        cfo_quality_component = self._cfo_quality_component(company_id)
        if cfo_quality_component is not None:
            components.append(cfo_quality_component)

        if not components:
            return None

        return round(sum(components) / len(components), 2)

    def _scale_between(
        self,
        value: Any,
        lower_bound: float,
        upper_bound: float,
    ) -> float | None:
        """Convert a value into a 0-100 score across a bounded range."""

        if value is None:
            return None

        numeric_value = float(value)
        bounded_value = min(max(numeric_value, lower_bound), upper_bound)
        return round(
            ((bounded_value - lower_bound) / (upper_bound - lower_bound)) * 100,
            2,
        )

    def _cfo_quality_component(self, company_id: Any) -> float | None:
        """Convert the existing CFO quality helper into a numeric score."""

        company_records = self.company_history.get(company_id, [])

        if len(company_records) < 5:
            return None

        recent_records = company_records[-5:]
        avg_cfo = sum(
            self._safe_number(item["cashflow"]["operating_activity"])
            for item in recent_records
        ) / len(recent_records)
        avg_pat = sum(
            self._safe_number(item["pnl"]["net_profit"]) for item in recent_records
        ) / len(recent_records)

        score = cfo_quality_score(avg_cfo, avg_pat)
        if score is None:
            return None

        label_to_score = {
            "High Quality": 100.0,
            "Moderate": 70.0,
            "Accrual Risk": 30.0,
        }
        return label_to_score.get(score[1], 50.0)


if __name__ == "__main__":
    engine = RatioEngine()
    try:
        engine.load_data()
        engine.prepare_data()
        engine.calculate_ratios()
        engine.save_to_database()
        engine.print_sample_companies(3)
    finally:
        engine.close()
