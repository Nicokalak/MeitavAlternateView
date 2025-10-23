import http
import unittest

from meitav_view.app import app


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_app_loads(self):
        response = self.app.get("/health")
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
