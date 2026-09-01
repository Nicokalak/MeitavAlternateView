import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from meitav_view.app import app
from meitav_view.model.watchlist import WatchlistItem


class MeitavViewTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("meitav_view.app.viewer")
    def test_watchlist_get_endpoint(self, mock_viewer: MagicMock) -> None:
        mock_viewer.get_watchlist_items.return_value = [
            WatchlistItem(symbol="AAPL", quantity=10, cost=150.0),
            WatchlistItem(symbol="MSFT", quantity=0, cost=0.0),
        ]
        response = self.client.get("/watchList")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {"symbol": "AAPL", "quantity": 10, "cost": 150.0},
                {"symbol": "MSFT", "quantity": 0, "cost": 0.0},
            ],
        )

    @patch("meitav_view.app.viewer")
    def test_watchlist_post_valid_string_list(self, mock_viewer: MagicMock) -> None:
        payload = ["AAPL", "MSFT"]
        response = self.client.post("/watchList", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Watchlist updated successfully"})
        mock_viewer.save_watchlist.assert_called_once_with(
            [
                WatchlistItem(symbol="AAPL", quantity=0, cost=0.0),
                WatchlistItem(symbol="MSFT", quantity=0, cost=0.0),
            ]
        )

    @patch("meitav_view.app.viewer")
    def test_watchlist_post_valid_object_list(self, mock_viewer: MagicMock) -> None:

        payload = [
            {"symbol": "AAPL", "quantity": 10, "cost": 150.5},
            {"symbol": "NVDA", "qty": 5, "cost": 120.0},
        ]
        response = self.client.post("/watchList", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Watchlist updated successfully"})
        mock_viewer.save_watchlist.assert_called_once_with(
            [
                WatchlistItem(symbol="AAPL", quantity=10, cost=150.5),
                WatchlistItem(symbol="NVDA", quantity=5, cost=120.0),
            ]
        )

    def test_watchlist_post_invalid_data(self) -> None:
        payload = {"invalid": "data"}
        response = self.client.post("/watchList", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_root_endpoint(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    @patch("meitav_view.app.viewer")
    def test_trends_endpoint_with_mock_auth(self, mock_viewer: MagicMock) -> None:
        mock_viewer.get_trends.return_value = {"trend1": "value1", "trend2": "value2"}
        response = self.client.get("/trends", headers={"X-Email": "allowed@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_viewer.get_trends.return_value)

    @patch("meitav_view.app.viewer")
    def test_marketstate_endpoint_with_mock(self, mock_viewer: MagicMock) -> None:
        mock_viewer.get_market_state.return_value = {"market": "open"}
        response = self.client.get("/marketState", headers={"X-Email": "allowed@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_viewer.get_market_state.return_value)

    @patch("meitav_view.app.viewer")
    def test_marketstate_endpoint_with_runtime_error(self, mock_viewer: MagicMock) -> None:
        mock_viewer.get_market_state.side_effect = RuntimeError("error")
        response = self.client.get("/marketState", headers={"X-Email": "allowed@example.com"})
        self.assertEqual(response.status_code, 500)

    @patch("meitav_view.app.viewer")
    def test_portfolio_endpoint_with_mock(self, mock_viewer: MagicMock) -> None:
        mock_viewer.enrich_portfolio.return_value = []
        response = self.client.get("/portfolio", headers={"X-Email": "allowed@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    @patch("meitav_view.app.viewer")
    def test_portfolio_endpoint_with_connection_error(self, mock_viewer: MagicMock) -> None:
        mock_viewer.enrich_portfolio.side_effect = ConnectionError("conn error")
        response = self.client.get("/portfolio", headers={"X-Email": "allowed@example.com"})
        self.assertEqual(response.status_code, 500)

    @patch("meitav_view.app.viewer")
    def test_ticker_endpoint_with_mock(self, mock_viewer: MagicMock) -> None:
        mock_viewer.get_current_market_state_key.return_value = "post"
        mock_viewer.find_stock.return_value = {"symbol": "AAPL", "price": 150}
        response = self.client.get("/ticker/AAPL", headers={"X-Email": "allowed@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "stock": {"symbol": "AAPL", "price": 150},
                "market-state-4calc": "post",
            },
        )

    @patch("meitav_view.utils.auth_utils.Config")
    def test_auth_success_with_allowed_users(self, mock_config_cls: MagicMock) -> None:
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = ["allowed@example.com"]
        mock_config_cls.return_value = mock_config_instance

        with patch("meitav_view.app.viewer") as mock_viewer:
            mock_viewer.get_trends.return_value = {"ok": True}
            response = self.client.get("/trends", headers={"X-Email": "allowed@example.com"})
            self.assertEqual(response.status_code, 200)

    @patch("meitav_view.utils.auth_utils.Config")
    def test_auth_failure_no_email_with_allowed_users(self, mock_config_cls: MagicMock) -> None:
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = ["allowed@example.com"]
        mock_config_cls.return_value = mock_config_instance

        response = self.client.get("/trends")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Unauthorized"})

    @patch("meitav_view.utils.auth_utils.Config")
    def test_auth_failure_wrong_email_with_allowed_users(self, mock_config_cls: MagicMock) -> None:
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = ["allowed@example.com"]
        mock_config_cls.return_value = mock_config_instance

        response = self.client.get("/trends", headers={"X-Email": "not_allowed@example.com"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Unauthorized"})

    def test_static_files_served(self) -> None:
        css_response = self.client.get("/css/main.css")
        self.assertEqual(css_response.status_code, 200)

        js_response = self.client.get("/js/app.js")
        self.assertEqual(js_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
