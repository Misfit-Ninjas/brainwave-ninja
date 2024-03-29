import pytest
from polars.testing import assert_frame_equal

from backend.services.neurons.financial import symbols


# Note for future self when we want to start cashing def funcname(self, parameter_list):
# https://stackoverflow.com/questions/16463582/memoize-to-disk-python-persistent-memoization


class TestRun:
    @pytest.fixture
    def stock_results(self):
        return symbols.DataSchema.DataFrame(
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
        )

    @pytest.fixture
    def market_find_all(self, mocker):
        return mocker.patch("services.web.financial_modeling_prep.market.find_all", autospec=True)

    @pytest.fixture(autouse=True)
    def stock_find_all(self, mocker, stock_results):
        find_all = mocker.patch(
            "services.web.financial_modeling_prep.stock.find_all", autospec=True
        )
        find_all.return_value = stock_results
        return find_all

    class TestWhenCountryIsGiven:
        def test_it_should_narrow_down_based_on_the_market(self, market_find_all):
            config = symbols.Config(country="United States of America")
            market_find_all.return_value = ["NASDAQ"]
            symbols.run(config)
            market_find_all.assert_called_once_with(country="United States of America")

    class TestWhenMarketIsGiven:
        def test_it_should_pass_value_to_the_stock_finder(self, stock_find_all, stock_results):
            config = symbols.Config(market="NASDAQ")
            result = symbols.run(config)
            stock_find_all.assert_called_once_with(exchange="NASDAQ", sector=None, industry=None)
            assert_frame_equal(result, stock_results)

    class TestWhenCountryAndMarketIsGiven:
        @pytest.mark.parametrize(
            "markets, expected_market", [(["NASDAQ", "NYSE"], "NASDAQ"), (["raisins"], None)]
        )
        def test_it_should_take_the_intersection(
            self, stock_find_all, market_find_all, markets, expected_market
        ):
            config = symbols.Config(country="United States of America", market="NASDAQ")
            market_find_all.return_value = markets
            result = symbols.run(config)
            if expected_market:
                stock_find_all.assert_called_once_with(
                    exchange=expected_market, industry=None, sector=None
                )
            else:
                stock_find_all.assert_not_called()
                assert result.is_empty()

    class TestWhenSectorIsGiven:
        def test_it_should_pass_value_to_the_stock_finder(self, stock_find_all, stock_results):
            config = symbols.Config(sector="Technology")
            result = symbols.run(config)
            stock_find_all.assert_called_once_with(
                sector="Technology", industry=None, exchange=None
            )
            assert_frame_equal(result, stock_results)

    class TestWhenIndustryIsGiven:
        def test_it_should_pass_value_to_the_stock_finder(self, stock_find_all, stock_results):
            config = symbols.Config(industry="Consumer Electronics")
            result = symbols.run(config)
            stock_find_all.assert_called_once_with(
                industry="Consumer Electronics", sector=None, exchange=None
            )
            assert_frame_equal(result, stock_results)

    class TestWhenSymbolIsGiven:
        def test_it_should_use_that_value(self, mocker, stock_find_all, stock_results):
            config = symbols.Config(symbol="AAPL")
            profile = mocker.patch(
                "services.web.financial_modeling_prep.stock.profile", autospec=True
            )
            profile.return_value = stock_results[0]
            result = symbols.run(config)
            stock_find_all.assert_not_called()
            profile.assert_called_once_with("AAPL")
            assert_frame_equal(result, stock_results)
