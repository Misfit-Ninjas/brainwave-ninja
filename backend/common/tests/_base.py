import django.test
import django.urls

import rest_framework.test
from model_bakery import baker


class TestCase(django.test.TestCase):
    def setUp(self):
        self._user_password = "123456"
        self.user = baker.prepare("users.User", email="user@email.com")
        self.user.set_password(self._user_password)
        self.user.save()

        self.auth_client = django.test.Client()
        self.auth_client.login(email=self.user.email, password=self._user_password)

    def reverse(self, name, *args, **kwargs):
        """Reverse a url, convenience to avoid having to import reverse in tests"""
        return django.urls.reverse(name, args=args, kwargs=kwargs)


class APITestCase(rest_framework.test.APITestCase, TestCase):
    pass


class RequiresAuthenticatedUserMixin:
    def test_get_requires_authenticated_user(self):
        response = self.client.get(self.view_url)
        self.assertResponse403(response)


class AuthGetRequestSuccessMixin:
    def test_auth_get_success(self):
        response = self.auth_client.get(self.view_url)
        self.assertResponse200(response)
