from polars.testing import assert_frame_equal
import pytest
from services.web.financial_modeling_prep import income_statement


class TestAnnual:
    @pytest.fixture
    def api_results(self, datadir_obj):
        return datadir_obj.load("restapi-result.json")

    @pytest.fixture
    def expected_results(self, datadir_obj):
        return income_statement.DataSchema.DataFrame(datadir_obj.load("py-result.yaml"))

    @pytest.fixture
    def income_statement(self, httpserver):
        return income_statement.IncomeStatement(
            api_key="1234567890", session_throttle=999, api_endpoint=httpserver.url_for("/")
        )

    @pytest.fixture
    def function(self, income_statement):
        return income_statement.annual

    def test_it_should_make_the_right_api_request(
        self, httpserver, function, api_results, expected_results
    ):
        httpserver.expect_oneshot_request(
            "/api/v3/income-statement/AAPL",
            query_string=dict(apikey="1234567890", period=function.__name__, method="GET"),
        ).respond_with_json(api_results)
        result = function("AAPL")
        assert_frame_equal(result, expected_results)
        httpserver.check_assertions()


class TestQuarter(TestAnnual):
    @pytest.fixture
    def function(self, income_statement):
        return income_statement.quarter
