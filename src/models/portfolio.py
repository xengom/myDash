"""Portfolio data model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Portfolio:
    """Portfolio data model.

    Attributes:
        id: Portfolio ID (None for new portfolios)
        name: Portfolio name
        created_at: Creation timestamp
        updated_at: Last update timestamp
        stocks: List of stocks in portfolio (optional)
        total_value: Current total value (calculated)
        total_cost: Total cost basis (calculated)
        value_gain_overall: Total gain/loss (calculated)
        value_gain_today: Today's gain/loss (calculated)
        change_percent: Today's percentage change (calculated)
    """

    name: str
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    stocks: list["Stock"] = field(default_factory=list)
    total_value: float = 0.0
    total_cost: float = 0.0
    value_gain_overall: float = 0.0
    value_gain_today: float = 0.0
    change_percent: float = 0.0

    def __str__(self) -> str:
        """String representation."""
        return f"Portfolio(id={self.id}, name='{self.name}', value=${self.total_value:.2f})"

    def __repr__(self) -> str:
        """Developer representation."""
        return self.__str__()


# Forward reference for type hints
from src.models.stock import Stock

Portfolio.__annotations__['stocks'] = list[Stock]
