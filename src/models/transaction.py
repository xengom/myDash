"""Transaction data model."""

from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum


class TransactionType(Enum):
    """Transaction type enumeration."""

    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Transaction:
    """Transaction data model.

    Attributes:
        id: Transaction ID (None for new transactions)
        stock_id: Parent stock ID
        txn_type: Transaction type (BUY or SELL)
        quantity: Number of shares
        price: Price per share
        txn_date: Transaction date
        created_at: Creation timestamp
    """

    stock_id: int
    txn_type: TransactionType
    quantity: float
    price: float
    txn_date: date
    id: int | None = None
    created_at: datetime | None = None

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Transaction(id={self.id}, type={self.txn_type.value}, "
            f"qty={self.quantity}, price=${self.price:.2f})"
        )

    def __repr__(self) -> str:
        """Developer representation."""
        return self.__str__()

    @property
    def total_value(self) -> float:
        """Calculate total transaction value."""
        return self.quantity * self.price
