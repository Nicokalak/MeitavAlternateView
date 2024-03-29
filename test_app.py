import unittest
from app import app


class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_app_loads(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
