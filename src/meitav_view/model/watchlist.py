"""Watchlist item data model."""

from typing import Any

from pydantic import AliasChoices, BaseModel, Field


class WatchlistItem(BaseModel):
    """Model representing an item in the user's watchlist."""

    symbol: str
    quantity: int = Field(default=0, validation_alias=AliasChoices("quantity", "qty", "Qty"))
    cost: float = 0.0

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }

    @classmethod
    def from_entry(cls, entry: Any) -> "WatchlistItem":
        """Convert a raw dictionary, string, or WatchlistItem into a WatchlistItem instance."""
        if isinstance(entry, str):
            return cls(symbol=entry.strip().upper(), quantity=0, cost=0.0)
        if isinstance(entry, dict):
            symbol = str(entry.get("symbol", entry.get("Symbol", ""))).strip().upper()
            qty_raw = entry.get("quantity", entry.get("qty", entry.get("Qty", 0)))
            cost_raw = entry.get("cost", entry.get("Cost", entry.get("Average Cost", 0.0)))
            try:
                qty = int(qty_raw) if qty_raw is not None else 0
            except (ValueError, TypeError):
                qty = 0
            try:
                cost = float(cost_raw) if cost_raw is not None else 0.0
            except (ValueError, TypeError):
                cost = 0.0
            return cls(symbol=symbol, quantity=max(0, qty), cost=max(0.0, cost))
        if isinstance(entry, cls):
            return entry
        raise ValueError(f"Invalid watchlist entry: {entry}")
