import unittest
from unittest.mock import MagicMock, patch

from meitav_view.model.stock import Stock
from meitav_view.model.watchlist import WatchlistItem
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

    def test_get_market_state_ignores_watchlist_for_dollar_gainers_losers(self) -> None:
        portfolio_stock = MagicMock(spec=Stock)
        portfolio_stock.symbol = "AAPL"
        portfolio_stock.type = "E"
        portfolio_stock.quantity = 10
        portfolio_stock.gain = 2.0
        portfolio_stock.api_data = {
            "marketState": "REGULAR",
            "regularMarketChange": 5.0,  # 5.0 * 10 = $50
            "regularMarketChangePercent": 2.0,
            "regularMarketVolume": 1000,
            "averageDailyVolume10Day": 500,
        }

        watchlist_stock = MagicMock(spec=Stock)
        watchlist_stock.symbol = "NVDA"
        watchlist_stock.type = "W"
        watchlist_stock.quantity = 100
        watchlist_stock.gain = 10.0
        watchlist_stock.api_data = {
            "marketState": "REGULAR",
            "regularMarketChange": 10.0,  # 10.0 * 100 = $1000 (higher than AAPL)
            "regularMarketChangePercent": 15.0,  # 15% (higher than AAPL)
            "regularMarketVolume": 5000,
            "averageDailyVolume10Day": 2000,
        }

        self.viewer._stocks = [portfolio_stock, watchlist_stock]
        result = self.viewer.get_market_state()

        # Top gainer ($) must be the portfolio stock AAPL (ignoring watchlist NVDA)
        self.assertEqual(result["top-gainer"], portfolio_stock)
        # Top gainer (%) keeps % including watchlist
        self.assertEqual(result["top-gainer%"], watchlist_stock)

    def test_get_watchlist_items_mixed_formats(self) -> None:
        self.viewer.config.get.return_value = [
            "AAPL",
            {"symbol": "MSFT", "quantity": 10, "cost": 400.0},
            {"Symbol": "NVDA", "Qty": 5, "Average Cost": 120.0},
            12345,  # invalid, should be skipped with warning
        ]
        items = self.viewer.get_watchlist_items()
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].symbol, "AAPL")
        self.assertEqual(items[0].quantity, 0)
        self.assertEqual(items[0].cost, 0.0)
        self.assertEqual(items[1].symbol, "MSFT")
        self.assertEqual(items[1].quantity, 10)
        self.assertEqual(items[1].cost, 400.0)
        self.assertEqual(items[2].symbol, "NVDA")
        self.assertEqual(items[2].quantity, 5)
        self.assertEqual(items[2].cost, 120.0)

        # test property watchlist
        self.assertEqual(self.viewer.watchlist, {"AAPL", "MSFT", "NVDA"})

    def test_save_watchlist(self) -> None:
        items = [
            WatchlistItem(symbol="AAPL", quantity=10, cost=150.0),
            WatchlistItem(symbol="GOOG", quantity=0, cost=0.0),
        ]
        self.viewer.save_watchlist(items)
        self.viewer.config.set_and_save.assert_called_once_with(
            "watch_list",
            [
                {"symbol": "AAPL", "quantity": 10, "cost": 150.0},
                {"symbol": "GOOG", "quantity": 0, "cost": 0.0},
            ],
        )

    def test_enrich_portfolio_with_watchlist_item_attributes(self) -> None:
        self.viewer.get_portfolio_data = MagicMock(return_value=[])  # type: ignore[assignment]
        self.viewer.get_watchlist_items = MagicMock(  # type: ignore[assignment]
            return_value=[
                WatchlistItem(symbol="AAPL", quantity=10, cost=100.0),
                WatchlistItem(symbol="MSFT", quantity=0, cost=0.0),
            ]
        )
        self.viewer.yahoo_requestor.request.return_value = [
            {
                "symbol": "AAPL",
                "marketState": "REGULAR",
                "regularMarketPrice": 120.0,
                "regularMarketChange": 5.0,
            },
            {
                "symbol": "MSFT",
                "marketState": "REGULAR",
                "regularMarketPrice": 300.0,
                "regularMarketChange": -2.0,
            },
        ]
        stocks = self.viewer.enrich_portfolio()
        self.assertEqual(len(stocks), 2)

        aapl = next(s for s in stocks if s.symbol == "AAPL")
        self.assertEqual(aapl.type, "W")
        self.assertEqual(aapl.quantity, 10)
        self.assertEqual(aapl.cost, 100.0)
        self.assertEqual(aapl.last_price, 120.0)
        self.assertEqual(aapl.day_val, 50.0)  # 5.0 * 10
        self.assertEqual(aapl.total_val, 1200.0)  # 120.0 * 10
        self.assertEqual(aapl.total_change, 200.0)  # (120 - 100) * 10
        self.assertEqual(aapl.gain, 20.0)  # ((120 - 100) / 100) * 100
        self.assertEqual(aapl.total_cost, 1000.0)  # 1200 - 200

        msft = next(s for s in stocks if s.symbol == "MSFT")
        self.assertEqual(msft.type, "W")
        self.assertEqual(msft.quantity, 0)
        self.assertIsNone(msft.cost)
        self.assertEqual(msft.last_price, 300.0)
        self.assertEqual(msft.day_val, -2.0)
        self.assertEqual(msft.total_val, 0.0)
        self.assertEqual(msft.total_change, 0.0)
        self.assertEqual(msft.gain, 0.0)
