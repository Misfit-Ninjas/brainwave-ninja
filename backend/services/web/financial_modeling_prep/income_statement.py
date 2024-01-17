from services.util import Schema
from ._base import Base as _Base
from ._base import CONFIG

DataSchema = Schema(
    # Look inside py-results.yaml for the fields / types
)


class IncomeStatement(_Base):
    def annual(self, symbol: str) -> pl.DataFrame:
        pass

    def quarter(self, symbol: str) -> pl.DataFrame:
        pass


_income_statement = IncomeStatement(**CONFIG)
annual = _income_statement.annual
quarter = _income_statement.quarter
