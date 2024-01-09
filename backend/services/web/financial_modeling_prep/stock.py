from collections.abc import Iterator
from typing import TypedDict

from ._base import CONFIG
from ._base import Base as _Base


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


class Stock(_Base):
    def find_all(
        self,
        sector: str | None = None,
        industry: str | None = None,
        exchange: str | None = None,
        is_actively_trading: bool = True,
    ) -> Iterator[Results]:
        # WARNING: The `screener` API call from FPM seems to limit us to ~1k results
        # at a time. This is a known limitation we're accepting for now

        if not any([sector, industry, exchange]):
            return

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

        for item in result:
            yield {
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

    def profile(self, symbol: str) -> Results | None:
        result = self.get(f"/api/v3/profile/{symbol}").json()
        if result:
            return {
                "symbol": result[0]["symbol"],
                "company_name": result[0]["companyName"],
                "sector": result[0]["sector"],
                "industry": result[0]["industry"],
                "exchange": result[0]["exchange"],
                "exchange_short_name": result[0]["exchangeShortName"],
                "country": result[0]["country"],
                "is_etf": result[0]["isEtf"],
                "is_actively_trading": result[0]["isActivelyTrading"],
            }


_stock = Stock(**CONFIG)
find_all = _stock.find_all
profile = _stock.profile
