from collections.abc import Iterable

import polars as pl
from more_itertools import peekable


class Schema:
    def __init__(self, **kwargs):
        self.dict = kwargs
        self.columns = set(kwargs)
        self.polars = self.DataFrame(validate=False).schema

    def validate(self, data: peekable):
        try:
            data_cols = set(data.peek())
        except StopIteration:
            pass
        else:
            if cols := self.columns - data_cols:
                raise ValueError(f"Missing columns: {cols}")
            if cols := data_cols - self.columns:
                raise ValueError(f"Got extra columns: {cols}")

    def DataFrame(self, data: Iterable[dict] | None = None, validate: bool = True) -> pl.DataFrame:  # noqa: N802
        if validate and data:
            data = peekable(data)
            self.validate(data)
        ds = pl.DataFrame(data, self.dict)
        return ds
