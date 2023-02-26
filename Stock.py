from json import JSONEncoder


class Stock(object):
    def __init__(self, d: dict):
        super().__init__()
        self.symbol: str = d.get('Symbol')
        self.quantity: int = d.get('Qty', 0)
        self.change: float = d.get('Change', 0)
        self.last_price: float = d.get('Last', 0)
        self.day_val: float = d['Day\'s Value']
        self.cost: float = d.get('Average Cost', None)
        self.gain: float = d.get('Gain')
        self.total_change: float = d.get('Profit/ Loss', None)
        self.total_val: float = d.get('Value', None)
        self.type: str = d['Entry Type']
        self.expiration: str = d.get('Expiration', None)
        self.strike: float = d.get('Strike', None)
        self.p_or_c: str = d.get('Put/ Call', None)
        self.percent_change: float = self.__calc_percent_change()
        self.principle_change: float = 0 if self.change == 0 or self.cost is None else (self.change / self.cost) * 100
        self.weight: float = 0
        self.api_data: dict = {}

    def __calc_percent_change(self):
        if self.change == 0:
            return 0
        elif float(self.last_price) - float(self.change) == 0:
            return (float(self.change) / (float(self.last_price) - float(self.change) + 0.0001)) * 100
        else:
            return float(self.change) / (float(self.last_price) - float(self.change)) * 100

    def __str__(self):
        return self.symbol

    def set_weight(self, portfolio_total_val):
        self.weight = (self.total_val / portfolio_total_val) * 100

    def set_api_data(self, api_data):
        if api_data['symbol'] == self.symbol:
            self.api_data = api_data
        else:
            raise ValueError("unmatch Symbols {} {}".format(self.symbol, api_data['symbol']))


class StockEncoder(JSONEncoder):
    def default(self, o):
        if type(o) is Stock:
            return o.__dict__
        elif type(o) is set:
            return list(o)
        else:
            raise TypeError("not supported type {}".format(type(o)))
