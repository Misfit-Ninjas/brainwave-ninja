import os
import pathlib
from collections.abc import Iterator

import jsonlines


with jsonlines.open(pathlib.Path(os.path.realpath(__file__)).parent / "exchanges.jsonl") as f:
    EXCHANGES = list(f)


def find_all(country: str) -> Iterator[str]:
    country = country.strip()
    for exchange in EXCHANGES:
        if exchange["country"] == country:
            yield from exchange["FMP"]
