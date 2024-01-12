import itertools
import os
import pathlib

import jsonlines
import polars as pl


with jsonlines.open(pathlib.Path(os.path.realpath(__file__)).parent / "exchanges.jsonl") as f:
    EXCHANGES = pl.DataFrame(f)


def find_all(country: str) -> list[str]:
    return list(itertools.chain(*EXCHANGES.filter(pl.col("country") == country)["FMP"].to_list()))
