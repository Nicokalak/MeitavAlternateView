from dataclasses import dataclass
from typing import Any


@dataclass()
class Stock:
    symbol: str
    quantity: int
    change: float
    last_price: float
    day_val: float
    cost: float | None
    total_cost: float
    gain: float
    total_change: float
    total_val: float
    type: str
    expiration: str | None
    strike: float | None
    p_or_c: str | None
    percent_change: float
    principle_change: float
    api_data: dict[str, Any]
    weight: float = 0

    def __init__(self, d: dict[str, Any]):
        super().__init__()
        self.symbol = str(d.get("Symbol"))
        self.quantity = d.get("Qty", 0)
        self.change = d.get("Change", 0)
        self.last_price = d.get("Last", -1)
        self.day_val = d["Day's Value"]
        self.cost = d.get("Average Cost")
        self.gain = d.get("Gain", 0)
        self.total_change = d.get("Profit/ Loss", 0)
        self.total_val = d.get("Value", 0)
        self.type = d.get("Entry Type", "E")
        self.expiration = d.get("Expiration")
        self.strike = d.get("Strike")
        self.p_or_c = d.get("Put/ Call")
        self.percent_change = self.__calc_percent_change()
        self.principle_change = 0 if self.change == 0 or self.cost is None else (self.change / self.cost) * 100
        self.total_cost = self.total_val - self.total_change
        self.api_data = {}

    def __repr__(self) -> str:
        return self.symbol

    def __calc_percent_change(self) -> float:
        if self.change == 0:
            return 0
        if float(self.last_price) - float(self.change) == 0:
            return (float(self.change) / (float(self.last_price) - float(self.change) + 0.0001)) * 100
        return float(self.change) / (float(self.last_price) - float(self.change)) * 100

    def set_weight(self, portfolio_total_val: float) -> None:
        self.weight = (self.total_val / portfolio_total_val) * 100

    def set_api_data(self, api_data: dict[str, Any]) -> None:
        if api_data and api_data["symbol"] == self.symbol:
            self.api_data = api_data
        else:
            raise ValueError("unmatch Symbols {} {}".format(self.symbol, api_data["symbol"]))
