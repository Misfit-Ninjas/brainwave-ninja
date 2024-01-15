"""This filters a list of financial symbols by various metrics and turns the ones that pass over the speicifed time range."""

from dataclasses import dataclass

import polars as pl

from services.web.financial_modeling_prep import balance_sheet, ratios
from services.web.financial_modeling_prep.stock import DataSchema  # noqa


@dataclass
class Config:
    # Profitability ratios
    return_on_equity_min: int | float = float("-inf")
    return_on_equity_max: int | float = float("inf")
    return_on_assets_min: int | float = float("-inf")
    return_on_assets_max: int | float = float("inf")
    # Liquidy ratios
    current_ratio_min: float = float("-inf")
    current_ratio_max: float = float("inf")
    acid_test_ratio_min: float = float("-inf")
    acid_test_ratio_max: float = float("inf")
    # Effeciency ratios
    inventory_turnover_min: int | float = float("-inf")
    inventory_turnover_max: int | float = float("inf")
    receivables_turnover_min: int | float = float("-inf")
    receivables_turnover_max: int | float = float("inf")
    # Solvancy ratios
    debt_to_equity_ratio_min: float = float("-inf")
    debt_to_equity_ratio_max: float = float("inf")
    liabilities_to_equity_ratio_min: float = float("-inf")
    liabilities_to_equity_ratio_max: float = float("inf")


def run(
    config: Config,
    symbol_results: pl.DataFrame,
    quarters_results: pl.DataFrame,
) -> pl.DataFrame:
    valid_quarters = quarters_results[["calendar_year", "period"]].unique()

    symbols = set()
    for symbol in symbol_results["symbol"].to_list():
        # fmt: off
        df = (
            ratios.quarter(symbol)
            .join(balance_sheet.quarter(symbol), on=["calendar_year", "period"])
            .join(valid_quarters, on=["calendar_year", "period"])
            .mean()
            .with_columns(
                [
                    # debt_to_equity_ratio = (long_term_debt + short_term_debt) / total_stockholders_equity
                    (
                        (pl.col("long_term_debt") + pl.col("short_term_debt")) / pl.col("total_stockholders_equity")
                    ).alias("debt_to_equity_ratio"),

                    # liabilities_to_equity_ratio = total_liabilities / total_stockholders_equity
                    (
                        pl.col("total_liabilities") / pl.col("total_stockholders_equity")
                    ).alias("liabilities_to_equity_ratio"),

                    # acid_test_ratio = (total_assets - inventory) / total_liabilities
                    (
                        (pl.col("total_assets") - pl.col("inventory")) / pl.col("total_liabilities")
                    ).alias("acid_test_ratio"),
                ]
            )
            .filter(
                (config.return_on_equity_min <= pl.col("return_on_equity"))
                & (config.return_on_equity_max >= pl.col("return_on_equity"))
                & (config.return_on_assets_min <= pl.col("return_on_assets"))
                & (config.return_on_assets_max >= pl.col("return_on_assets"))
                & (config.current_ratio_min <= pl.col("current_ratio"))
                & (config.current_ratio_max >= pl.col("current_ratio"))
                & (config.acid_test_ratio_min <= pl.col("acid_test_ratio"))
                & (config.acid_test_ratio_max >= pl.col("acid_test_ratio"))
                & (config.inventory_turnover_min <= pl.col("inventory_turnover"))
                & (config.inventory_turnover_max >= pl.col("inventory_turnover"))
                & (config.receivables_turnover_min <= pl.col("receivables_turnover"))
                & (config.receivables_turnover_max >= pl.col("receivables_turnover"))
                & (config.debt_to_equity_ratio_min <= pl.col("debt_to_equity_ratio"))
                & (config.debt_to_equity_ratio_max >= pl.col("debt_to_equity_ratio"))
                & (config.liabilities_to_equity_ratio_min <= pl.col("liabilities_to_equity_ratio"))
                & (config.liabilities_to_equity_ratio_max >= pl.col("liabilities_to_equity_ratio"))
            )
        )
        # fmt: on
        if not df.is_empty():
            symbols.add(symbol)

    return symbol_results.filter(pl.col("symbol").is_in(symbols))
