"""Takes in a list of symbols and returns quarters for which financial reports are available"""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TypedDict

from services.neurons.financial import symbols
from services.web import financial_modeling_prep as fmp


@dataclass
class Config:
    start_quarter: str | None
    end_quarter: str | None


class Results(TypedDict):
    calendar_year: int
    period: str  # Q1, Q2, Q3, or Q4
    display: str  # "<calendar_year>-<period>"


def run(config: Config, symbol_results: Iterator[symbols.Results]) -> Iterator[Results]:
    result = set()
    for symbol in symbol_results:
        for balance_sheet in fmp.balance_sheet.quarter(symbol["symbol"]):
            result.add(
                (
                    balance_sheet["calendar_year"],
                    balance_sheet["period"],
                    f"{balance_sheet['calendar_year']}-{balance_sheet['period']}",
                )
            )
    for calendar_year, period, display in sorted(result):
        if (not config.start_quarter or config.start_quarter <= display) and (
            not config.end_quarter or display <= config.end_quarter
        ):
            yield {"calendar_year": calendar_year, "period": period, "display": display}
