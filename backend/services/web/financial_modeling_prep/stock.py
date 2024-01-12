import polars as pl
from services.util import Schema

from ._base import CONFIG
from ._base import Base as _Base


DataSchema = Schema(
    symbol=str,
    company_name=str,
    sector=str,
    industry=str,
    exchange=str,
    exchange_short_name=str,
    country=str,
    is_etf=bool,
    is_actively_trading=bool,
)


class Stock(_Base):
    def find_all(
        self,
        sector: str | None = None,
        industry: str | None = None,
        exchange: str | None = None,
        is_actively_trading: bool = True,
    ) -> pl.DataFrame:
        # WARNING: The `screener` API call from FPM seems to limit us to ~1k results
        # at a time. This is a known limitation we're accepting for now

        if not any([sector, industry, exchange]):
            return DataSchema.DataFrame()

        payload = dict(isActivelyTrading="true")
        if sector is not None:
            payload["sector"] = sector
        if industry is not None:
            payload["industry"] = industry
        if exchange is not None:
            payload["exchange"] = exchange
        if is_actively_trading is not None:
            payload["isActivelyTrading"] = str(is_actively_trading).lower()

        result = self.get("/api/v3/stock-screener", **payload).json()

        return DataSchema.DataFrame(
            {
                "symbol": item["symbol"],
                "company_name": item["companyName"],
                "sector": item["sector"],
                "industry": item["industry"],
                "exchange": item["exchange"],
                "exchange_short_name": item["exchangeShortName"],
                "country": item["country"],
                "is_etf": item["isEtf"],
                "is_actively_trading": item["isActivelyTrading"],
            }
            for item in result
        )

    def profile(self, symbol: str) -> pl.DataFrame:
        result = self.get(f"/api/v3/profile/{symbol}").json()
        return DataSchema.DataFrame(
            {
                "symbol": item["symbol"],
                "company_name": item["companyName"],
                "sector": item["sector"],
                "industry": item["industry"],
                "exchange": item["exchange"],
                "exchange_short_name": item["exchangeShortName"],
                "country": item["country"],
                "is_etf": item["isEtf"],
                "is_actively_trading": item["isActivelyTrading"],
            }
            for item in result
        )


_stock = Stock(**CONFIG)
find_all = _stock.find_all
profile = _stock.profile
