import pytest
from polars.testing import assert_frame_equal
from services.neurons.financial import quarters, symbols
from services.tests.conftest import TEST_ROOT, Datadir
from services.web.financial_modeling_prep import balance_sheet


class TestRun:
    class TestWhenGivenAListOfSymbols:
        def test_it_should_return_the_correct_quarters(self, mocker):
            datadir_obj = Datadir(
                TEST_ROOT / "web" / "financial_modeling_prep" / "test_balance_sheet"
            )
            quarter = mocker.patch(
                "services.web.financial_modeling_prep.balance_sheet.quarter", autospec=True
            )
            quarter.return_value = balance_sheet.DataSchema.DataFrame(
                datadir_obj.load("py-result.yaml"),
            )

            result = quarters.run(
                config=quarters.Config(),
                symbol_results=symbols.DataSchema.DataFrame(
                    [
                        {
                            "symbol": "AAPL",
                            "company_name": "Apple Inc.",
                            "sector": "Technology",
                            "industry": "Consumer Electronics",
                            "exchange": "NASDAQ Global Select",
                            "exchange_short_name": "NASDAQ",
                            "country": "US",
                            "is_etf": False,
                            "is_actively_trading": True,
                        }
                    ],
                ),
            )
            assert_frame_equal(
                result,
                quarters.DataSchema.DataFrame(
                    [{"calendar_year": 2022, "period": "Q4", "display": "2022-Q4"}],
                ),
            )

    class TestWhenGivenAConfig:
        @pytest.fixture(autouse=True)
        def quarter(self, mocker):
            quarter = mocker.patch(
                "services.web.financial_modeling_prep.balance_sheet.quarter", autospec=True
            )
            quarter.return_value = quarters.DataSchema.DataFrame(
                [
                    {"calendar_year": 2023, "period": "Q1", "display": "2023-Q1"},
                    {"calendar_year": 2023, "period": "Q2", "display": "2023-Q2"},
                    {"calendar_year": 2023, "period": "Q3", "display": "2023-Q3"},
                    {"calendar_year": 2023, "period": "Q4", "display": "2023-Q4"},
                ],
            )

        def test_it_should_respect_the_start(self):
            result = quarters.run(
                config=quarters.Config(start_year=2023, start_quarter=quarters.QuarterEnum.Q3),
                symbol_results=symbols.DataSchema.DataFrame(
                    [
                        {
                            "symbol": "AAPL",
                            "company_name": "Apple Inc.",
                            "sector": "Technology",
                            "industry": "Consumer Electronics",
                            "exchange": "NASDAQ Global Select",
                            "exchange_short_name": "NASDAQ",
                            "country": "US",
                            "is_etf": False,
                            "is_actively_trading": True,
                        }
                    ],
                ),
            )
            assert_frame_equal(
                result,
                quarters.DataSchema.DataFrame(
                    [
                        {"calendar_year": 2023, "period": "Q3", "display": "2023-Q3"},
                        {"calendar_year": 2023, "period": "Q4", "display": "2023-Q4"},
                    ],
                ),
            )

        def test_it_should_respect_the_end(self):
            result = quarters.run(
                config=quarters.Config(end_year=2023, end_quarter=quarters.QuarterEnum.Q2),
                symbol_results=symbols.DataSchema.DataFrame(
                    [
                        {
                            "symbol": "AAPL",
                            "company_name": "Apple Inc.",
                            "sector": "Technology",
                            "industry": "Consumer Electronics",
                            "exchange": "NASDAQ Global Select",
                            "exchange_short_name": "NASDAQ",
                            "country": "US",
                            "is_etf": False,
                            "is_actively_trading": True,
                        }
                    ],
                ),
            )
            assert_frame_equal(
                result,
                quarters.DataSchema.DataFrame(
                    [
                        {"calendar_year": 2023, "period": "Q1", "display": "2023-Q1"},
                        {"calendar_year": 2023, "period": "Q2", "display": "2023-Q2"},
                    ],
                ),
            )
