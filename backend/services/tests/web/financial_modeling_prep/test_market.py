from services.web.financial_modeling_prep import market


class TestFindAll:
    class TestWhenAValidCountryIsPassedIn:
        def test_it_should_return_a_list_of_FMP_markets(self):
            result = market.find_all("United States of America")
            assert result == ["ASE", "AMEX", "ETF", "NASDAQ", "NYSE"]

    class TestWhenAnInvalidCountryIsPassedIn:
        def test_it_should_return_nothing(self):
            assert not market.find_all("raisins")
