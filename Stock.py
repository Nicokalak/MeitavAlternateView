from json import JSONEncoder


class Stock(object):
    def __init__(self, d: dict):
        super().__init__()
        self.symbol = d['Symbol']
        self.quantity = d['Qty']
        self.change = d['Change']
        self.last_price = d['Last']
        self.day_val = d['Day\'s Value']
        self.cost = Stock.__init_from_dict('Average Cost', d)
        self.gain = d['Gain']
        self.total_change = Stock.__init_from_dict('Profit/ Loss', d)
        self.total_val = Stock.__init_from_dict('Value', d)
        self.type = d['Entry Type']
        self.expiration = Stock.__init_from_dict('Expiration', d)
        self.strike = Stock.__init_from_dict('Strike', d)
        self.p_or_c = Stock.__init_from_dict('Put/ Call', d)
        self.percent_change = self.__calc_percent_change()
        self.principle_change = 0 if self.change == 0 or self.cost is None else (self.change / self.cost) * 100
        self.weight = 0

    @staticmethod
    def __init_from_dict(key, d):
        return d[key] if key in d else None

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


class StockEncoder(JSONEncoder):
    def default(self, o):
        if type(o) is Stock:
            return o.__dict__
        elif type(o) is set:
            return list(o)
        else:
            raise TypeError("not supported type {}".format(type(o)))
