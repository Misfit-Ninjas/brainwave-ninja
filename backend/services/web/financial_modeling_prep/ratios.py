import datetime
from collections.abc import Iterator

import polars as pl
import stringcase
from services.util import Schema

from ._base import CONFIG
from ._base import Base as _Base


DataSchema = Schema(
    asset_turnover=float,
    calendar_year=int,
    capital_expenditure_coverage_ratio=float,
    cash_conversion_cycle=float,
    cash_flow_coverage_ratios=float,
    cash_flow_to_debt_ratio=float,
    cash_per_share=float,
    cash_ratio=float,
    company_equity_multiplier=float,
    current_ratio=float,
    date=datetime.date,
    days_of_inventory_outstanding=float,
    days_of_payables_outstanding=float,
    days_of_sales_outstanding=float,
    debt_equity_ratio=float,
    debt_ratio=float,
    dividend_paid_and_capex_coverage_ratio=float,
    dividend_payout_ratio=float,
    dividend_yield=float,
    ebit_per_revenue=float,
    ebt_per_ebit=float,
    effective_tax_rate=float,
    enterprise_value_multiple=float,
    fixed_asset_turnover=float,
    free_cash_flow_operating_cash_flow_ratio=float,
    free_cash_flow_per_share=float,
    gross_profit_margin=float,
    interest_coverage=float,
    inventory_turnover=float,
    long_term_debt_to_capitalization=float,
    net_income_per_ebt=float,
    net_profit_margin=float,
    operating_cash_flow_per_share=float,
    operating_cash_flow_sales_ratio=float,
    operating_cycle=float,
    operating_profit_margin=float,
    payables_turnover=float,
    payout_ratio=float,
    period=str,
    pretax_profit_margin=float,
    price_book_value_ratio=float,
    price_cash_flow_ratio=float,
    price_earnings_ratio=float,
    price_earnings_to_growth_ratio=float,
    price_fair_value=float,
    price_sales_ratio=float,
    price_to_book_ratio=float,
    price_to_free_cash_flows_ratio=float,
    price_to_operating_cash_flows_ratio=float,
    price_to_sales_ratio=float,
    quick_ratio=float,
    receivables_turnover=float,
    return_on_assets=float,
    return_on_capital_employed=float,
    return_on_equity=float,
    short_term_coverage_ratios=float,
    symbol=str,
    total_debt_to_capitalization=float,
)


class Ratios(_Base):
    def annual(self, symbol: str) -> pl.DataFrame:
        result = self.get(f"/api/v3/ratios/{symbol}", period="annual").json()
        return DataSchema.DataFrame(self._collect(result))

    def quarter(self, symbol: str) -> pl.DataFrame:
        result = self.get(f"/api/v3/ratios/{symbol}", period="quarter").json()
        return DataSchema.DataFrame(self._collect(result))

    def _collect(self, payload: list[dict]) -> Iterator[dict]:
        for item in payload:
            result_item = {stringcase.snakecase(key): value for key, value in item.items()}

            # Do type conversions
            result_item["date"] = datetime.datetime.strptime(result_item["date"], "%Y-%m-%d").date()
            result_item["calendar_year"] = int(result_item["calendar_year"])

            # fix keys that convert wrongly
            result_item["net_income_per_ebt"] = result_item.pop("net_income_per_e_b_t")

            yield result_item


_ratios = Ratios(**CONFIG)
annual = _ratios.annual
quarter = _ratios.quarter
