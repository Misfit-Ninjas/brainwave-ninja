import pytest
from services.web.financial_modeling_prep import stock


@pytest.fixture
def expected_results():
    return [
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
    ]


class TestFindAll:
    @pytest.fixture
    def api_results(self, datadir_obj):
        return datadir_obj.load("stock-screener.json")

    @pytest.fixture
    def base_http_req(self):
        return {"apikey": "1234567890", "isActivelyTrading": "true"}

    @pytest.fixture
    def stock(self, httpserver):
        return stock.Stock(
            api_key="1234567890", session_throttle=999, api_endpoint=httpserver.url_for("/")
        )

    class TestWhenSectorIsSpecified:
        def test_it_should_make_the_correct_API_request(
            self, stock, base_http_req, httpserver, api_results, expected_results
        ):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, sector="Technology"),
                method="GET",
            ).respond_with_json(api_results)

            results = list(stock.find_all(sector="Technology"))
            assert results == expected_results
            httpserver.check_assertions()

        def test_it_should_ignore_a_value_of_None(self, stock, httpserver):
            list(stock.find_all(sector=None))
            # Validate no requests have been made
            httpserver.check_assertions()

        def test_it_should_handle_empty_responses(self, stock, base_http_req, httpserver):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, sector="raisins"),
                method="GET",
            ).respond_with_json([])
            results = list(stock.find_all(sector="raisins"))
            assert results == []
            httpserver.check_assertions()

    class TestWhenIndustryIsSpecified:
        def test_it_should_make_the_correct_API_request(
            self, stock, base_http_req, httpserver, api_results, expected_results
        ):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, industry="Consumer Electronics"),
                method="GET",
            ).respond_with_json(api_results)

            print(httpserver.format_matchers())
            results = list(stock.find_all(industry="Consumer Electronics"))
            assert results == expected_results
            httpserver.check_assertions()

        def test_it_should_ignore_a_value_of_None(self, stock, httpserver):
            list(stock.find_all(sector=None))
            # Validate no requests have been made
            httpserver.check_assertions()

        def test_it_should_handle_empty_responses(self, stock, base_http_req, httpserver):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, sector="raisins"),
                method="GET",
            ).respond_with_json([])
            results = list(stock.find_all(sector="raisins"))
            assert results == []
            httpserver.check_assertions()

    class TestWhenExchangeIsSpecified:
        def test_it_should_make_the_correct_API_request(
            self, stock, base_http_req, httpserver, api_results, expected_results
        ):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, exchange="NASDAQ"),
                method="GET",
            ).respond_with_json(api_results)

            results = list(stock.find_all(exchange="NASDAQ"))
            assert results == expected_results
            httpserver.check_assertions()

        def test_it_should_ignore_a_value_of_None(self, stock, httpserver):
            list(stock.find_all(exchange=None))
            # Validate no requests have been made
            httpserver.check_assertions()

        def test_it_should_handle_empty_responses(self, stock, base_http_req, httpserver):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, exchange="raisins"),
                method="GET",
            ).respond_with_json([])
            results = list(stock.find_all(exchange="raisins"))
            assert results == []
            httpserver.check_assertions()

    class TestWhenIsActivelyTradingSpecified:
        def test_it_should_default_to_true(self, stock, base_http_req, httpserver):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, sector="raisins"),
                method="GET",
            ).respond_with_json([])

            list(stock.find_all())
            httpserver.check_assertions()

        def test_it_should_accept_false(self, stock, base_http_req, httpserver):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, sector="raisins", isActivelyTrading="false"),
                method="GET",
            ).respond_with_json([])

            list(stock.find_all(sector="raisins", is_actively_trading=False))
            httpserver.check_assertions()


class TestProfile:
    @pytest.fixture
    def stock(self, httpserver):
        return stock.Stock(
            api_key="1234567890", session_throttle=999, api_endpoint=httpserver.url_for("/")
        )

    class TestWhenSymbolIsSpecified:
        @pytest.fixture
        def api_results(self, datadir_obj):
            return datadir_obj.load("profile.json")

        def test_it_should_make_the_correct_API_request(
            self, stock, httpserver, api_results, expected_results
        ):
            httpserver.expect_oneshot_request(
                "/api/v3/profile/AAPL",
                query_string=dict(apikey="1234567890"),
                method="GET",
            ).respond_with_json(api_results)
            results = stock.profile(symbol="AAPL")
            print(httpserver.format_matchers())
            assert results == expected_results[0]
            httpserver.check_assertions()

        def test_it_should_handle_empty_responses(self, stock, httpserver):
            httpserver.expect_oneshot_request(
                "/api/v3/profile/raisins",
                query_string=dict(apikey="1234567890"),
                method="GET",
            ).respond_with_json([])
            results = stock.profile(symbol="raisins")
            assert results is None
            httpserver.check_assertions()
