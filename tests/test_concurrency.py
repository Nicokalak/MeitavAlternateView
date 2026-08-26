import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from meitav_view.app import app
from meitav_view.model.stock import Stock
from meitav_view.viewer import MeitavViewer


class TestMeitavViewerConcurrency(unittest.TestCase):
    @patch("meitav_view.viewer.Config")
    @patch("meitav_view.viewer.TrendPersist")
    @patch("meitav_view.viewer.YahooRequestor")
    def test_concurrent_reads_and_atomic_updates(
        self,
        _mock_yahoo: MagicMock,
        _mock_trends: MagicMock,
        _mock_config: MagicMock,
    ) -> None:
        viewer = MeitavViewer()

        def make_stock(symbol: str, state: str) -> Stock:
            s = MagicMock(spec=Stock)
            s.symbol = symbol
            s.quantity = 10
            s.gain = 1.0
            s.api_data = {
                "marketState": state,
                "preMarketChange": 1.0,
                "preMarketChangePercent": 1.0,
                "regularMarketChange": 1.0,
                "regularMarketChangePercent": 1.0,
                "postMarketChange": 1.0,
                "postMarketChangePercent": 1.0,
                "regularMarketVolume": 100,
                "averageDailyVolume10Day": 100,
            }
            return s

        viewer._stocks = [make_stock("INIT", "REGULAR")]

        def reader_task() -> None:
            for _ in range(50):
                key = viewer.get_current_market_state_key()
                self.assertIn(key, ("pre", "regular", "post"))
                state = viewer.get_market_state()
                self.assertIn(state["marketState"], ("PRE", "REGULAR", "POST"))

        def writer_task(state: str) -> None:
            for i in range(50):
                viewer._stocks = [make_stock(f"STOCK_{i}", state)]

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(reader_task),
                executor.submit(reader_task),
                executor.submit(writer_task, "PRE"),
                executor.submit(writer_task, "REGULAR"),
                executor.submit(writer_task, "POST"),
                executor.submit(reader_task),
            ]
            for f in futures:
                f.result()

    @patch("meitav_view.app.viewer")
    def test_lifespan_enrichment_on_startup(self, mock_viewer: MagicMock) -> None:
        with TestClient(app) as client:
            response = client.get("/health")
            self.assertEqual(response.status_code, 200)
            mock_viewer.enrich_portfolio.assert_called_once()
