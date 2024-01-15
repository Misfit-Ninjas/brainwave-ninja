"""fetches stock symbols"""

from dataclasses import dataclass

import polars as pl

from services.web import financial_modeling_prep as fmp
from services.web.financial_modeling_prep.stock import DataSchema


@dataclass
class Config:
    country: str | None = None
    market: str | None = None
    sector: str | None = None
    industry: str | None = None
    symbol: str | None = None


def run(config: Config) -> pl.DataFrame:
    if config.symbol:
        # If a symbol is given, there's no point continuing
        # with any of the other selectors
        return fmp.stock.profile(config.symbol)

    markets = [config.market]
    if config.country:
        # If we're given the country, we have to convert that
        # to a market first. We want to find stocks listed in that country's
        # stock exchanges, not stocks with mailing addresses in that country
        markets = fmp.market.find_all(country=config.country)

    # Only continue if the country and market match
    if config.market and markets:
        if not (markets := list(set(markets) & {config.market})):
            return DataSchema.DataFrame()

    return pl.concat(
        [
            fmp.stock.find_all(
                sector=config.sector if config.sector else None,
                industry=config.industry if config.industry else None,
                exchange=market,
            )
            for market in markets or [None]  # If markets is not set, just send `None`
        ]
    )
