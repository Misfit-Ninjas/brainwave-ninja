import pytest
from services.web.financial_modeling_prep import balance_sheet


class TestAnnual:
    @pytest.fixture
    def api_results(self, datadir_obj):
        return datadir_obj.load("balance-sheet.json")

    @pytest.fixture
    def expected_results(self, datadir_obj):
        return datadir_obj.load("balance-sheet.yaml")

    @pytest.fixture
    def balance_sheet(self, httpserver):
        return balance_sheet.BalanceSheet(
            api_key="1234567890", session_throttle=999, api_endpoint=httpserver.url_for("/")
        )

    @pytest.fixture
    def balance_sheet_fn(self, balance_sheet):
        return balance_sheet.annual

    def test_it_should_make_the_right_api_request(
        self, httpserver, api_results, balance_sheet_fn, expected_results
    ):
        httpserver.expect_oneshot_request(
            "/api/v3/balance-sheet-statement/AAPL",
            query_string=dict(apikey="1234567890", period=balance_sheet_fn.__name__),
            method="GET",
        ).respond_with_json(api_results)
        result = list(balance_sheet_fn("AAPL"))
        assert result == expected_results
        httpserver.check_assertions()


class TestQuarter(TestAnnual):
    @pytest.fixture
    def balance_sheet_fn(self, balance_sheet):
        return balance_sheet.quarter
