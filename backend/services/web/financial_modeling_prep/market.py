import itertools
import pathlib

import jsonlines
import pandas


with jsonlines.open(pathlib.Path(__file__).parent / "exchanges.jsonl") as f:
    EXCHANGES = pandas.DataFrame(f)


def find_all(country: str) -> list[str]:
    return list(itertools.chain(*EXCHANGES[EXCHANGES.country == country.strip()].FMP.to_list()))
