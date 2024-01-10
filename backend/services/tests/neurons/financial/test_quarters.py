from typing import cast

import pytest
from services.neurons.financial import quarters, symbols
from services.tests.conftest import Datadir


class TestRun:
    class TestWhenGivenAListOfSymbols:
        def test_it_should_return_the_correct_quarters(self, mocker, test_root):
            datadir_obj = Datadir(
                test_root / "web" / "financial_modeling_prep" / "test_balance_sheet"
            )
            quarter = mocker.patch(
                "services.web.financial_modeling_prep.balance_sheet.quarter", autospec=True
            )
            quarter.return_value = datadir_obj.load("balance-sheet.yaml")

            result = list(
                quarters.run(
                    config=quarters.Config(None, None),
                    symbol_results=iter([cast(symbols.Results, {"symbol": "AAPL"})]),
                )
            )
            assert result == [{"calendar_year": 2022, "period": "Q4", "display": "2022-Q4"}]

    class TestWhenGivenAConfig:
        @pytest.fixture(autouse=True)
        def quarter(self, mocker):
            quarter = mocker.patch(
                "services.web.financial_modeling_prep.balance_sheet.quarter", autospec=True
            )
            quarter.return_value = [
                {"calendar_year": 2023, "period": "Q1", "display": "2023-Q1"},
                {"calendar_year": 2023, "period": "Q2", "display": "2023-Q2"},
                {"calendar_year": 2023, "period": "Q3", "display": "2023-Q3"},
                {"calendar_year": 2023, "period": "Q4", "display": "2023-Q4"},
            ]

        def test_it_should_respect_the_start(self):
            result = list(
                quarters.run(
                    config=quarters.Config("2023-Q3", None),
                    symbol_results=iter([cast(symbols.Results, {"symbol": "AAPL"})]),
                )
            )
            assert result == [
                {"calendar_year": 2023, "period": "Q3", "display": "2023-Q3"},
                {"calendar_year": 2023, "period": "Q4", "display": "2023-Q4"},
            ]

        def test_it_should_respect_the_end(self):
            result = list(
                quarters.run(
                    config=quarters.Config(None, "2023-Q2"),
                    symbol_results=iter([cast(symbols.Results, {"symbol": "AAPL"})]),
                )
            )
            assert result == [
                {"calendar_year": 2023, "period": "Q1", "display": "2023-Q1"},
                {"calendar_year": 2023, "period": "Q2", "display": "2023-Q2"},
            ]
