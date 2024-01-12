"""Takes in a list of symbols and returns quarters for which financial reports are available"""

import enum
from dataclasses import dataclass

import polars as pl

from services.util import Schema
from services.web import financial_modeling_prep as fmp


class QuarterEnum(enum.Enum):
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"


@dataclass
class Config:
    start_year: int = 0
    start_quarter: QuarterEnum = QuarterEnum.Q1
    end_year: int = 65_535
    end_quarter: QuarterEnum = QuarterEnum.Q4


DataSchema = Schema(
    calendar_year=int,
    period=str,  # Q1, Q2, Q3, or Q4
    display=str,  # "<calendar_year>-<period>"
)


def run(config: Config, symbol_results: pl.DataFrame) -> pl.DataFrame:
    df = DataSchema.DataFrame()

    for symbol in symbol_results["symbol"].to_list():
        df = pl.concat(
            [
                df,
                (
                    fmp.balance_sheet.quarter(symbol)[["calendar_year", "period"]]
                    .filter(
                        (config.start_year <= pl.col("calendar_year"))
                        & (config.end_year >= pl.col("calendar_year"))
                        & (config.start_quarter.value <= pl.col("period"))
                        & (config.end_quarter.value >= pl.col("period"))
                    )
                    .with_columns(
                        pl.concat_str(
                            [pl.col("calendar_year"), pl.col("period")], separator="-"
                        ).alias("display")
                    )
                ),
            ]
        )
    return df
