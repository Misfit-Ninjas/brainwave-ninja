import pytest
from polars.testing import assert_frame_equal
from services.web.financial_modeling_prep import ratios


class TestAnnual:
    @pytest.fixture
    def api_results(self, datadir_obj):
        return datadir_obj.load("restapi-result.json")

    @pytest.fixture
    def expected_results(self, datadir_obj):
        return ratios.DataSchema.DataFrame(datadir_obj.load("py-result.yaml"))

    @pytest.fixture
    def ratios(self, httpserver):
        return ratios.Ratios(
            api_key="1234567890", session_throttle=999, api_endpoint=httpserver.url_for("/")
        )

    @pytest.fixture
    def ratios_fn(self, ratios):
        return ratios.annual

    def test_it_should_make_the_right_api_request(
        self, httpserver, api_results, ratios_fn, expected_results
    ):
        httpserver.expect_oneshot_request(
            "/api/v3/ratios/AAPL",
            query_string=dict(apikey="1234567890", period=ratios_fn.__name__),
            method="GET",
        ).respond_with_json(api_results)
        result = ratios_fn("AAPL")
        assert_frame_equal(result, expected_results)
        httpserver.check_assertions()


class TestQuarter(TestAnnual):
    @pytest.fixture
    def balance_sheet_fn(self, balance_sheet):
        return balance_sheet.quarter
