import datetime
from collections.abc import Iterable
from typing import TypedDict, cast

import stringcase

from ._base import CONFIG
from ._base import Base as _Base


class Results(TypedDict):
    date: datetime.date
    symbol: str
    reported_currency: str
    cik: str
    filling_date: datetime.date
    accepted_date: datetime.datetime
    calendar_year: int
    period: str  # FY, Q1, Q2, Q3, or Q4
    cash_and_cash_equivalents: int
    short_term_investments: int
    cash_and_short_term_investments: int
    net_receivables: int
    inventory: int
    other_current_assets: int
    total_current_assets: int
    property_plant_equipment_net: int
    goodwill: int
    intangible_assets: int
    goodwill_and_intangible_assets: int
    long_term_investments: int
    tax_assets: int
    other_non_current_assets: int
    total_non_current_assets: int
    other_assets: int
    total_assets: int
    account_payables: int
    short_term_debt: int
    tax_payables: int
    deferred_revenue: int
    other_current_liabilities: int
    total_current_liabilities: int
    long_term_debt: int
    deferred_revenue_non_current: int
    deferred_tax_liabilities_non_current: int
    other_non_current_liabilities: int
    total_non_current_liabilities: int
    other_liabilities: int
    capital_lease_obligations: int
    total_liabilities: int
    preferred_stock: int
    common_stock: int
    retained_earnings: int
    accumulated_other_comprehensive_income_loss: int
    othertotal_stockholders_equity: int
    total_stockholders_equity: int
    total_equity: int
    total_liabilities_and_stockholders_equity: int
    minority_interest: int
    total_liabilities_and_total_equity: int
    total_investments: int
    total_debt: int
    net_debt: int
    link: str
    final_link: str


class BalanceSheet(_Base):
    def annual(self, symbol: str) -> Iterable[Results]:
        result = self.get(f"/api/v3/balance-sheet-statement/{symbol}", period="annual").json()
        return self._convert(result)

    def quarter(self, symbol: str) -> Iterable[Results]:
        result = self.get(f"/api/v3/balance-sheet-statement/{symbol}", period="quarter").json()
        return self._convert(result)

    def _convert(self, payload: list[dict]) -> Iterable[Results]:
        for item in payload:
            result_item = {stringcase.snakecase(key): value for key, value in item.items()}

            # Do type conversions
            result_item["calendar_year"] = int(result_item["calendar_year"])
            result_item["date"] = datetime.datetime.strptime(result_item["date"], "%Y-%m-%d").date()
            result_item["filling_date"] = datetime.datetime.strptime(
                result_item["filling_date"], "%Y-%m-%d"
            ).date()
            result_item["accepted_date"] = datetime.datetime.strptime(
                result_item["accepted_date"], "%Y-%m-%d %H:%M:%S"
            )
            yield cast(Results, result_item)


_balance_sheet = BalanceSheet(**CONFIG)
annual = _balance_sheet.annual
quarter = _balance_sheet.quarter
