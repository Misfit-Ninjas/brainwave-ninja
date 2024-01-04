from common.tests._base import APITestCase, TestCase


class TestIndexView(TestCase):
    view_name = "common:index"

    def test_returns_status_200(self):
        response = self.auth_client.get(self.reverse(self.view_name))
        assert response.status_code == 200


class TestBrainAPI(APITestCase, TestCase):
    view_name = "Brain-results"

    def test_execute_returns_ok(self):
        response = self.client.post(
            self.reverse(self.view_name, guid="cb457b38-a8d0-4c84-9887-520992a876d5"), format="json"
        )
        assert response.status_code == 200
        assert response.json()["result"] == "OK"
