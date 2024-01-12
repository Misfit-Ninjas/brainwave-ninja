from collections.abc import Callable

import polars as pl
import pytest
from polars.testing import assert_frame_equal
from services.neurons.financial import metrics_filter, quarters, symbols
from services.tests.conftest import TEST_ROOT, Datadir

from backend.services.web.financial_modeling_prep import balance_sheet, ratios


class TestRun:
    class BaseTest:
        MIN = symbols.DataSchema.DataFrame(
            [
                {
                    "symbol": "MIN",
                    "company_name": "Minimum Inc.",
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                    "exchange": "NASDAQ Global Select",
                    "exchange_short_name": "NASDAQ",
                    "country": "United States of America",
                    "is_etf": True,
                    "is_actively_trading": True,
                },
            ]
        )
        MAX = symbols.DataSchema.DataFrame(
            [
                {
                    "symbol": "MAX",
                    "company_name": "Maximum Inc.",
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                    "exchange": "NASDAQ Global Select",
                    "exchange_short_name": "NASDAQ",
                    "country": "United States of America",
                    "is_etf": True,
                    "is_actively_trading": True,
                },
            ]
        )

        def make_ratios(self, **kwargs) -> pl.DataFrame:
            ratio_data = Datadir(TEST_ROOT / "web" / "financial_modeling_prep" / "test_ratios")
            return dict(ratio_data.load("py-result.yaml")[0], **kwargs)

        def make_balance_sheet(self, **kwargs) -> pl.DataFrame:
            ratio_data = Datadir(
                TEST_ROOT / "web" / "financial_modeling_prep" / "test_balance_sheet"
            )
            return dict(ratio_data.load("py-result.yaml")[0], **kwargs)

        def balance_sheet_under_555(self):
            # If needed, test scnearios overwrite this with their own implementation
            return balance_sheet.DataSchema.DataFrame(
                [
                    self.make_balance_sheet(calendar_year=2023, period="Q3"),
                    self.make_balance_sheet(calendar_year=2023, period="Q4"),
                ]
            )

        def balance_sheet_over_555(self):
            # If needed, test scnearios overwrite this with their own implementation
            return balance_sheet.DataSchema.DataFrame(
                [
                    self.make_balance_sheet(calendar_year=2023, period="Q3"),
                    self.make_balance_sheet(calendar_year=2023, period="Q4"),
                ]
            )

        def expect(self, *specs) -> Callable:
            def handler(*args, **kwargs):
                for spec, results in specs:
                    if args == spec or args == kwargs or args == (args, kwargs):
                        return results
                raise RuntimeError(
                    f"Received unexpected function parameters: {args=} {kwargs=} {specs=}"
                )

            return handler

        @pytest.fixture(autouse=True)
        def mock_quarter_ratios(self, mocker, attribute):
            service = mocker.patch(
                "services.web.financial_modeling_prep.ratios.quarter", autospec=True
            )
            service.side_effect = self.expect(
                (
                    ("MAX",),
                    # These are below the max (555)
                    ratios.DataSchema.DataFrame(
                        [
                            self.make_ratios(
                                **{attribute: 100.0, "calendar_year": 2023, "period": "Q3"}
                            ),
                            self.make_ratios(
                                **{attribute: 200.0, "calendar_year": 2023, "period": "Q4"}
                            ),
                        ],
                        validate=False,  # Just silently drop `attribute` is it isn't in the table
                    ),
                ),
                (
                    ("MIN",),
                    # These are above the min (555)
                    ratios.DataSchema.DataFrame(
                        [
                            self.make_ratios(
                                **{attribute: 800.0, "calendar_year": 2023, "period": "Q3"}
                            ),
                            self.make_ratios(
                                **{attribute: 900.0, "calendar_year": 2023, "period": "Q4"}
                            ),
                        ],
                        validate=False,  # Just silently drop `attribute` is it isn't in the table
                    ),
                ),
            )

        @pytest.fixture(autouse=True)
        def mock_balance_sheet(self, mocker, attribute):
            service = mocker.patch(
                "services.web.financial_modeling_prep.balance_sheet.quarter", autospec=True
            )
            service.side_effect = self.expect(
                (
                    ("MAX",),
                    # These are below the max (555)
                    self.balance_sheet_under_555(),
                ),
                (
                    ("MIN",),
                    # These are above the min (555)
                    self.balance_sheet_over_555(),
                ),
            )

        def do_filtering(
            self,
            config: metrics_filter.Config,
            quarters_results: pl.DataFrame | None = None,
        ) -> pl.DataFrame:
            return metrics_filter.run(
                config=config,
                symbol_results=pl.concat([self.MIN, self.MAX]),
                quarters_results=(
                    quarters_results
                    if quarters_results is not None
                    else quarters.DataSchema.DataFrame(
                        [
                            {"calendar_year": 2023, "period": "Q3", "display": "2023-Q3"},
                            {"calendar_year": 2023, "period": "Q4", "display": "2023-Q4"},
                        ],
                    )
                ),
            )

        def test_it_filters_min_properly(self, attribute: str):
            config = metrics_filter.Config(**{attribute + "_min": 555})
            result = self.do_filtering(config)
            assert_frame_equal(result, self.MIN)

        def test_it_filters_max_properly(self, attribute: str):
            config = metrics_filter.Config(**{attribute + "_max": 555})
            result = self.do_filtering(config)
            assert_frame_equal(result, self.MAX)

        def test_it_respects_quarters(self, attribute: str):
            config = metrics_filter.Config(**{attribute + "_min": 555})
            result = self.do_filtering(
                config,
                quarters_results=quarters.DataSchema.DataFrame(
                    [
                        # Neither of these quarters are in the mock data,
                        # so we should get nothing
                        {"calendar_year": 2023, "period": "Q1", "display": "2023-Q1"},
                        {"calendar_year": 2023, "period": "Q2", "display": "2023-Q2"},
                    ],
                ),
            )
            assert_frame_equal(result, metrics_filter.DataSchema.DataFrame())

    class TestWhenReturnOnEquityIsGiven(BaseTest):
        @pytest.fixture
        def attribute(self):
            return "return_on_equity"

    class TestWhenReturnOnAssetsIsGiven(BaseTest):
        @pytest.fixture
        def attribute(self):
            return "return_on_assets"

    class TestWhenCurrentRatioIsGiven(BaseTest):
        @pytest.fixture
        def attribute(self):
            return "current_ratio"

    class TestWhenAcidTestRatioIsGiven(BaseTest):
        @pytest.fixture
        def attribute(self):
            return "acid_test_ratio"

        def balance_sheet_under_555(self):
            return balance_sheet.DataSchema.DataFrame(
                [
                    self.make_balance_sheet(
                        total_assets=200,
                        inventory=100,
                        total_liabilities=300,
                        calendar_year=2023,
                        period="Q3",
                    ),
                    self.make_balance_sheet(
                        total_assets=400,
                        inventory=200,
                        total_liabilities=500,
                        calendar_year=2023,
                        period="Q4",
                    ),
                ]
            )

        def balance_sheet_over_555(self):
            return balance_sheet.DataSchema.DataFrame(
                [
                    self.make_balance_sheet(
                        total_assets=700,
                        inventory=0,
                        total_liabilities=1,
                        calendar_year=2023,
                        period="Q3",
                    ),
                    self.make_balance_sheet(
                        total_assets=900,
                        inventory=0,
                        total_liabilities=1,
                        calendar_year=2023,
                        period="Q4",
                    ),
                ]
            )

    class TestWhenInventoryTurnoverIsGiven(BaseTest):
        @pytest.fixture
        def attribute(self):
            return "inventory_turnover"

    class TestWhenReceivablesTurnoverIsGiven(BaseTest):
        @pytest.fixture
        def attribute(self):
            return "receivables_turnover"

    class TestWhenDebtToEquityIsGiven(BaseTest):
        @pytest.fixture
        def attribute(self):
            return "debt_to_equity_ratio"

        def balance_sheet_under_555(self):
            return balance_sheet.DataSchema.DataFrame(
                [
                    self.make_balance_sheet(
                        long_term_debt=100,
                        short_term_debt=200,
                        total_stockholders_equity=300,
                        calendar_year=2023,
                        period="Q3",
                    ),
                    self.make_balance_sheet(
                        long_term_debt=200,
                        short_term_debt=300,
                        total_stockholders_equity=400,
                        calendar_year=2023,
                        period="Q4",
                    ),
                ]
            )

        def balance_sheet_over_555(self):
            return balance_sheet.DataSchema.DataFrame(
                [
                    self.make_balance_sheet(
                        long_term_debt=400,
                        short_term_debt=500,
                        total_stockholders_equity=1,
                        calendar_year=2023,
                        period="Q3",
                    ),
                    self.make_balance_sheet(
                        long_term_debt=600,
                        short_term_debt=700,
                        total_stockholders_equity=1,
                        calendar_year=2023,
                        period="Q4",
                    ),
                ]
            )

    class TestWhenLiabilitiesToEquityRatioIsGiven(BaseTest):
        @pytest.fixture
        def attribute(self):
            return "liabilities_to_equity_ratio"

        def balance_sheet_under_555(self):
            return balance_sheet.DataSchema.DataFrame(
                [
                    self.make_balance_sheet(
                        total_liabilities=200,
                        total_stockholders_equity=100,
                        calendar_year=2023,
                        period="Q3",
                    ),
                    self.make_balance_sheet(
                        total_liabilities=300,
                        total_stockholders_equity=200,
                        calendar_year=2023,
                        period="Q4",
                    ),
                ]
            )

        def balance_sheet_over_555(self):
            return balance_sheet.DataSchema.DataFrame(
                [
                    self.make_balance_sheet(
                        total_liabilities=800,
                        total_stockholders_equity=1,
                        calendar_year=2023,
                        period="Q3",
                    ),
                    self.make_balance_sheet(
                        total_liabilities=900,
                        total_stockholders_equity=1,
                        calendar_year=2023,
                        period="Q4",
                    ),
                ]
            )
