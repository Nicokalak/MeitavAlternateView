import unittest
from unittest.mock import MagicMock, patch

from meitav_view.model.stock import Stock
from meitav_view.viewer import MeitavViewer


class TestMeitavViewer(unittest.TestCase):
    @patch("meitav_view.viewer.Config")
    @patch("meitav_view.viewer.TrendPersist")
    @patch("meitav_view.viewer.YahooRequestor")
    def setUp(self, _mock_yahoo: MagicMock, _mock_trends: MagicMock, _mock_config: MagicMock) -> None:
        self.viewer = MeitavViewer()

    def test_get_current_market_state_key_empty(self) -> None:
        self.viewer._stocks = []
        self.assertEqual(self.viewer.get_current_market_state_key(), "post")

    def test_get_current_market_state_key_pre(self) -> None:
        stock = MagicMock(spec=Stock)
        stock.api_data = {"marketState": "PRE"}
        self.viewer._stocks = [stock]
        self.assertEqual(self.viewer.get_current_market_state_key(), "pre")

    def test_get_current_market_state_key_regular(self) -> None:
        stock = MagicMock(spec=Stock)
        stock.api_data = {"marketState": "REGULAR"}
        self.viewer._stocks = [stock]
        self.assertEqual(self.viewer.get_current_market_state_key(), "regular")

    def test_get_current_market_state_key_prepre(self) -> None:
        stock = MagicMock(spec=Stock)
        stock.api_data = {"marketState": "PREPRE"}
        self.viewer._stocks = [stock]
        self.assertEqual(self.viewer.get_current_market_state_key(), "post")

    def test_find_stock_found_and_not_found(self) -> None:
        stock = MagicMock(spec=Stock)
        stock.symbol = "AAPL"
        self.viewer._stocks = [stock]

        # Test finding existing stock
        self.assertEqual(self.viewer.find_stock("AAPL"), stock)

        # Test finding non-existing stock returns None without error
        self.assertIsNone(self.viewer.find_stock("GOOG"))

    def test_get_market_state_empty_raises_error(self) -> None:
        self.viewer._stocks = []
        with self.assertRaises(RuntimeError):
            self.viewer.get_market_state()

    def test_get_market_state_valid(self) -> None:
        stock = MagicMock(spec=Stock)
        stock.symbol = "AAPL"
        stock.quantity = 10
        stock.gain = 5.0
        stock.api_data = {
            "marketState": "PRE",
            "preMarketChange": 2.5,
            "preMarketChangePercent": 1.2,
            "regularMarketVolume": 1000,
            "averageDailyVolume10Day": 500,
        }
        self.viewer._stocks = [stock]
        result = self.viewer.get_market_state()
        self.assertEqual(result["marketState"], "PRE")
        self.assertEqual(result["top-gainer"], stock)
        self.assertEqual(result["up-down"]["up"], 1)
        self.assertEqual(result["up-down"]["down"], 0)
