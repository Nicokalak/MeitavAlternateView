from unittest import TestCase

from Stock import Stock


class TestStock(TestCase):
    def test_stock_init(self):
        stock = Stock({
            'Symbol': 'test1',
            'Qty': 100,
            'Gain': 0.5,
            'Day\'s Value': 5.5,
            'Entry Type': 'W',
            'Last': 110,
            'Change': 10,
            'Value': 2000
        })
        api_data = {"symbol": "test1", 't': True}
        stock.set_weight(10000)
        stock.set_api_data(api_data)

        self.assertEqual('test1', stock.symbol)
        self.assertEqual(100, stock.quantity)
        self.assertEqual(0.5, stock.gain)
        self.assertEqual(5.5, stock.day_val)
        self.assertEqual('W', stock.type)
        self.assertEqual(110, stock.last_price)
        self.assertEqual(10, stock.percent_change)
        self.assertEqual(20, stock.weight)
        self.assertEqual(api_data, stock.api_data)

    def test_stock_init_badData(self):
        stock = Stock({
            'Symbol': 'test2',
            'Day\'s Value': 5.5,
            'Entry Type': 'W',
            'Last': -1,
            'Change': 0,
        })

        self.assertEqual('test2', stock.symbol)
        self.assertEqual(0, stock.quantity)
        self.assertEqual(0, stock.gain)
        self.assertEqual(5.5, stock.day_val)
        self.assertEqual('W', stock.type)
        self.assertEqual(0, stock.percent_change)


