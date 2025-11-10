"""Stock data model."""

from dataclasses import dataclass
from datetime import datetime, date


@dataclass
class Stock:
    """Stock data model.

    Attributes:
        id: Stock ID (None for new stocks)
        portfolio_id: Parent portfolio ID
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOG')
        purchase_date: Date of first purchase
        quantity: Total number of shares
        avg_price: Weighted average purchase price
        created_at: Creation timestamp
        updated_at: Last update timestamp
        current_price: Current market price (calculated)
        total_value: Current total value (quantity * current_price)
        total_cost: Total cost basis (quantity * avg_price)
        value_gain_overall: Total gain/loss (total_value - total_cost)
        value_gain_today: Today's gain/loss (calculated)
        change_percent: Today's percentage change (calculated)
    """

    symbol: str
    portfolio_id: int
    quantity: float
    avg_price: float
    purchase_date: date
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    current_price: float = 0.0
    total_value: float = 0.0
    total_cost: float = 0.0
    value_gain_overall: float = 0.0
    value_gain_today: float = 0.0
    change_percent: float = 0.0

    def __post_init__(self):
        """Calculate cost after initialization."""
        if self.total_cost == 0.0:
            self.total_cost = self.quantity * self.avg_price

    def __str__(self) -> str:
        """String representation."""
        return f"Stock(id={self.id}, symbol='{self.symbol}', qty={self.quantity}, avg=${self.avg_price:.2f})"

    def __repr__(self) -> str:
        """Developer representation."""
        return self.__str__()
