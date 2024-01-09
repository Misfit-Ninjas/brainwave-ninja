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


class TestFMPStockFindAll:
    @pytest.fixture
    def api_results(self):
        return [
            {
                "symbol": "AAPL",
                "companyName": "Apple Inc.",
                "marketCap": 2817856304000,
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "beta": 1.29,
                "price": 181.18,
                "lastAnnualDividend": 0.96,
                "volume": 61666311,
                "exchange": "NASDAQ Global Select",
                "exchangeShortName": "NASDAQ",
                "country": "US",
                "isEtf": False,
                "isActivelyTrading": True,
            }
        ]

    @pytest.fixture
    def base_http_req(self):
        return {"apikey": "1234567890", "isActivelyTrading": "true"}

    @pytest.fixture
    def stock(self, httpserver):
        return stock.Stock(
            api_key="1234567890", session_limit=999, api_endpoint=httpserver.url_for("/")
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

            results = stock.find_all(sector="Technology")
            assert results == expected_results
            httpserver.check_assertions()

        def test_it_should_ignore_a_value_of_None(self, stock, httpserver):
            stock.find_all(sector=None)
            # Validate no requests have been made
            httpserver.check_assertions()

        def test_it_should_handle_empty_responses(self, stock, base_http_req, httpserver):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, sector="raisins"),
                method="GET",
            ).respond_with_json([])
            results = stock.find_all(sector="raisins")
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
            results = stock.find_all(industry="Consumer Electronics")
            assert results == expected_results
            httpserver.check_assertions()

        def test_it_should_ignore_a_value_of_None(self, stock, httpserver):
            stock.find_all(sector=None)
            # Validate no requests have been made
            httpserver.check_assertions()

        def test_it_should_handle_empty_responses(self, stock, base_http_req, httpserver):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, sector="raisins"),
                method="GET",
            ).respond_with_json([])
            results = stock.find_all(sector="raisins")
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

            results = stock.find_all(exchange="NASDAQ")
            assert results == expected_results
            httpserver.check_assertions()

        def test_it_should_ignore_a_value_of_None(self, stock, httpserver):
            stock.find_all(exchange=None)
            # Validate no requests have been made
            httpserver.check_assertions()

        def test_it_should_handle_empty_responses(self, stock, base_http_req, httpserver):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, exchange="raisins"),
                method="GET",
            ).respond_with_json([])
            results = stock.find_all(exchange="raisins")
            assert results == []
            httpserver.check_assertions()

    class TestWhenIsActivelyTradingSpecified:
        def test_it_should_default_to_true(self, stock, base_http_req, httpserver):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, sector="raisins"),
                method="GET",
            ).respond_with_json([])

            stock.find_all()
            httpserver.check_assertions()

        def test_it_should_accept_false(self, stock, base_http_req, httpserver):
            httpserver.expect_oneshot_request(
                "/api/v3/stock-screener",
                query_string=dict(base_http_req, sector="raisins", isActivelyTrading="false"),
                method="GET",
            ).respond_with_json([])

            stock.find_all(sector="raisins", is_actively_trading=False)
            httpserver.check_assertions()


class TestFMPStockProfile:
    @pytest.fixture
    def stock(self, httpserver):
        return stock.Stock(
            api_key="1234567890", session_limit=999, api_endpoint=httpserver.url_for("/")
        )

    class TestWhenSymbolIsSpecified:
        @pytest.fixture
        def api_results(self):
            return [
                {
                    "symbol": "AAPL",
                    "price": 178.72,
                    "beta": 1.286802,
                    "volAvg": 58405568,
                    "mktCap": 2794144143933,
                    "lastDiv": 0.96,
                    "range": "124.17-198.23",
                    "changes": -0.13,
                    "companyName": "Apple Inc.",
                    "currency": "USD",
                    "cik": "0000320193",
                    "isin": "US0378331005",
                    "cusip": "037833100",
                    "exchange": "NASDAQ Global Select",
                    "exchangeShortName": "NASDAQ",
                    "industry": "Consumer Electronics",
                    "website": "https://www.apple.com",
                    "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. It also sells various related services. In addition, the company offers iPhone, a line of smartphones; Mac, a line of personal computers; iPad, a line of multi-purpose tablets; AirPods Max, an over-ear wireless headphone; and wearables, home, and accessories comprising AirPods, Apple TV, Apple Watch, Beats products, HomePod, and iPod touch. Further, it provides AppleCare support services; cloud services store services; and operates various platforms, including the App Store that allow customers to discover and download applications and digital content, such as books, music, video, games, and podcasts. Additionally, the company offers various services, such as Apple Arcade, a game subscription service; Apple Music, which offers users a curated listening experience with on-demand radio stations; Apple News+, a subscription news and magazine service; Apple TV+, which offers exclusive original content; Apple Card, a co-branded credit card; and Apple Pay, a cashless payment service, as well as licenses its intellectual property. The company serves consumers, and small and mid-sized businesses; and the education, enterprise, and government markets. It distributes third-party applications for its products through the App Store. The company also sells its products through its retail and online stores, and direct sales force; and third-party cellular network carriers, wholesalers, retailers, and resellers. Apple Inc. was incorporated in 1977 and is headquartered in Cupertino, California.",
                    "ceo": "Mr. Timothy D. Cook",
                    "sector": "Technology",
                    "country": "US",
                    "fullTimeEmployees": "164000",
                    "phone": "408 996 1010",
                    "address": "One Apple Park Way",
                    "city": "Cupertino",
                    "state": "CA",
                    "zip": "95014",
                    "dcfDiff": 4.15176,
                    "dcf": 150.082,
                    "image": "https://financialmodelingprep.com/image-stock/AAPL.png",
                    "ipoDate": "1980-12-12",
                    "defaultImage": False,
                    "isEtf": False,
                    "isActivelyTrading": True,
                    "isAdr": False,
                    "isFund": False,
                }
            ]

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
