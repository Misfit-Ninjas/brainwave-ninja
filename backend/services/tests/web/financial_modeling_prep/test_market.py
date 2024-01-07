from services.web.financial_modeling_prep import market


class TestFMPMarketFindAll:
    class TestWhenAValidCountryIsPassedIn:
        def test_it_should_return_a_list_of_FMP_markets(self):
            result = market.find_all("United States of America")
            assert result == ["ASE", "AMEX", "ETF", "NASDAQ", "NYSE"]

        def test_it_should_strip_spaces_before_doing_lookups(self):
            result1 = market.find_all("United States of America")
            result2 = market.find_all("     United States of America    ")
            assert result1 == result2

    class TestWhenAnInvalidCountryIsPassedIn:
        def test_it_should_return_nothing(self):
            assert market.find_all("raisins") == []
