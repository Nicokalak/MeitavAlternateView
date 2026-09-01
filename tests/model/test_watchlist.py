from unittest import TestCase

from meitav_view.model.watchlist import WatchlistItem


class TestWatchlistItem(TestCase):
    def test_watchlist_item_defaults(self) -> None:
        item = WatchlistItem(symbol="AAPL")
        self.assertEqual(item.symbol, "AAPL")
        self.assertEqual(item.quantity, 0)
        self.assertEqual(item.cost, 0.0)

    def test_watchlist_item_with_values(self) -> None:
        item = WatchlistItem(symbol="TSLA", quantity=15, cost=220.5)
        self.assertEqual(item.symbol, "TSLA")
        self.assertEqual(item.quantity, 15)
        self.assertEqual(item.cost, 220.5)

    def test_watchlist_item_alias_qty(self) -> None:
        item = WatchlistItem.model_validate({"symbol": "NVDA", "qty": 8, "cost": 115.0})
        self.assertEqual(item.symbol, "NVDA")
        self.assertEqual(item.quantity, 8)
        self.assertEqual(item.cost, 115.0)

    def test_from_entry_string(self) -> None:
        item = WatchlistItem.from_entry("aapl")
        self.assertEqual(item.symbol, "AAPL")
        self.assertEqual(item.quantity, 0)
        self.assertEqual(item.cost, 0.0)

    def test_from_entry_dict_full(self) -> None:
        item = WatchlistItem.from_entry({"symbol": "msft", "quantity": 12, "cost": 420.0})
        self.assertEqual(item.symbol, "MSFT")
        self.assertEqual(item.quantity, 12)
        self.assertEqual(item.cost, 420.0)

    def test_from_entry_dict_aliases(self) -> None:
        item = WatchlistItem.from_entry({"Symbol": "goog", "Qty": "5", "Average Cost": "175.5"})
        self.assertEqual(item.symbol, "GOOG")
        self.assertEqual(item.quantity, 5)
        self.assertEqual(item.cost, 175.5)

    def test_from_entry_dict_defaults_and_invalid(self) -> None:
        item = WatchlistItem.from_entry({"symbol": "amzn", "quantity": "invalid", "cost": None})
        self.assertEqual(item.symbol, "AMZN")
        self.assertEqual(item.quantity, 0)
        self.assertEqual(item.cost, 0.0)

    def test_from_entry_instance(self) -> None:
        original = WatchlistItem(symbol="META", quantity=3, cost=500.0)
        item = WatchlistItem.from_entry(original)
        self.assertEqual(item, original)

    def test_from_entry_invalid_type(self) -> None:
        with self.assertRaises(ValueError):
            WatchlistItem.from_entry(12345)
