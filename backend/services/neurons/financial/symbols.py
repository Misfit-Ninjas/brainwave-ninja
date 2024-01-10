"""fetches stock symbols"""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TypedDict

from services.web import financial_modeling_prep as fmp


@dataclass
class Config:
    country: str | None = None
    market: str | None = None
    sector: str | None = None
    industry: str | None = None
    symbol: str | None = None


class Results(TypedDict):
    symbol: str
    company_name: str
    sector: str
    industry: str
    exchange: str
    exchange_short_name: str
    country: str
    is_etf: bool
    is_actively_trading: bool


def run(config: Config) -> Iterator[Results]:
    if config.symbol:
        # If a symbol is given, there's no point continuing
        # with any of the other selectors
        if results := fmp.stock.profile(config.symbol):
            yield results
        return

    markets = list()
    if config.country:
        # If we're given the country, we have to convert that
        # to a market first. We want to find stocks listed in that country's
        # stock exchanges, not stocks with mailing addresses in that country
        markets = fmp.market.find_all(country=config.country)

    # Only continue if the country and market match
    if config.market:
        if not (markets := list(set(markets) & {config.market}) if markets else {config.market}):
            return

    for market in markets or [None]:  # If markets is not set, just send `None`
        # There can be multiple markets, so we need to loop through and union the results
        yield from fmp.stock.find_all(
            sector=config.sector if config.sector else None,
            industry=config.industry if config.industry else None,
            exchange=market,
        )
