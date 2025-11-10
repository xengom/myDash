"""Portfolio management service with weighted average calculation."""

from datetime import date, datetime
from typing import Optional

from src.database import DatabaseManager
from src.models import Portfolio, Stock, Transaction, TransactionType


class PortfolioManager:
    """Manages portfolio and stock operations with business logic."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize portfolio manager.

        Args:
            db_manager: Database manager instance (creates new if None)
        """
        self.db = db_manager or DatabaseManager()

    # ========== Portfolio Operations ==========

    def create_portfolio(self, name: str) -> Portfolio:
        """Create a new portfolio.

        Args:
            name: Portfolio name

        Returns:
            Created portfolio

        Raises:
            ValueError: If portfolio name is empty
            sqlite3.IntegrityError: If portfolio name already exists
        """
        if not name or not name.strip():
            raise ValueError("Portfolio name cannot be empty")

        return self.db.create_portfolio(name.strip())

    def get_all_portfolios(self) -> list[Portfolio]:
        """Get all portfolios.

        Returns:
            List of portfolios
        """
        return self.db.get_all_portfolios()

    def get_portfolio(self, portfolio_id: int) -> Optional[Portfolio]:
        """Get portfolio by ID with stocks.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            Portfolio with stocks or None if not found
        """
        portfolio = self.db.get_portfolio(portfolio_id)
        if portfolio:
            portfolio.stocks = self.db.get_stocks_by_portfolio(portfolio_id)
        return portfolio

    def update_portfolio(self, portfolio_id: int, name: str) -> Optional[Portfolio]:
        """Update portfolio name.

        Args:
            portfolio_id: Portfolio ID
            name: New portfolio name

        Returns:
            Updated portfolio or None if not found

        Raises:
            ValueError: If portfolio name is empty
        """
        if not name or not name.strip():
            raise ValueError("Portfolio name cannot be empty")

        return self.db.update_portfolio(portfolio_id, name.strip())

    def delete_portfolio(self, portfolio_id: int) -> bool:
        """Delete portfolio and all associated stocks.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            True if deleted, False if not found
        """
        return self.db.delete_portfolio(portfolio_id)

    # ========== Stock Operations ==========

    def add_stock(
        self,
        portfolio_id: int,
        symbol: str,
        quantity: float,
        price: float,
        purchase_date: Optional[date] = None
    ) -> Stock:
        """Add stock to portfolio or update with weighted average.

        If stock already exists in portfolio, calculates new weighted average price:
            new_avg = (existing_qty * existing_avg + new_qty * new_price) / (existing_qty + new_qty)

        Args:
            portfolio_id: Portfolio ID
            symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOG')
            quantity: Number of shares to add
            price: Purchase price per share
            purchase_date: Purchase date (default: today)

        Returns:
            Created or updated stock

        Raises:
            ValueError: If quantity or price is invalid
        """
        # Validate inputs
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price <= 0:
            raise ValueError("Price must be positive")
        if not symbol or not symbol.strip():
            raise ValueError("Symbol cannot be empty")

        symbol = symbol.strip().upper()
        purchase_date = purchase_date or date.today()

        # Check if stock already exists
        existing_stock = self.db.get_stock_by_symbol(portfolio_id, symbol)

        if existing_stock:
            # Calculate weighted average
            new_quantity = existing_stock.quantity + quantity
            new_avg_price = (
                (existing_stock.quantity * existing_stock.avg_price + quantity * price)
                / new_quantity
            )

            # Keep earliest purchase date
            earliest_date = min(existing_stock.purchase_date, purchase_date)

            # Update stock
            stock = self.db.update_stock(
                existing_stock.id,
                quantity=new_quantity,
                avg_price=new_avg_price,
                purchase_date=earliest_date
            )

            # Record transaction
            self.db.create_transaction(
                stock_id=stock.id,
                txn_type=TransactionType.BUY,
                quantity=quantity,
                price=price,
                txn_date=purchase_date
            )

            return stock

        else:
            # Create new stock
            stock = self.db.create_stock(
                portfolio_id=portfolio_id,
                symbol=symbol,
                quantity=quantity,
                avg_price=price,
                purchase_date=purchase_date
            )

            # Record transaction
            self.db.create_transaction(
                stock_id=stock.id,
                txn_type=TransactionType.BUY,
                quantity=quantity,
                price=price,
                txn_date=purchase_date
            )

            return stock

    def get_stocks(self, portfolio_id: int) -> list[Stock]:
        """Get all stocks in a portfolio.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            List of stocks
        """
        return self.db.get_stocks_by_portfolio(portfolio_id)

    def get_stock(self, stock_id: int) -> Optional[Stock]:
        """Get stock by ID.

        Args:
            stock_id: Stock ID

        Returns:
            Stock or None if not found
        """
        return self.db.get_stock(stock_id)

    def update_stock(
        self,
        stock_id: int,
        quantity: Optional[float] = None,
        avg_price: Optional[float] = None
    ) -> Optional[Stock]:
        """Update stock quantity or average price.

        Note: Direct updates bypass transaction history.
        Consider using add_stock() for tracked purchases.

        Args:
            stock_id: Stock ID
            quantity: New quantity (optional)
            avg_price: New average price (optional)

        Returns:
            Updated stock or None if not found

        Raises:
            ValueError: If quantity or price is invalid
        """
        if quantity is not None and quantity <= 0:
            raise ValueError("Quantity must be positive")
        if avg_price is not None and avg_price <= 0:
            raise ValueError("Price must be positive")

        return self.db.update_stock(stock_id, quantity=quantity, avg_price=avg_price)

    def delete_stock(self, stock_id: int) -> bool:
        """Delete stock and all associated transactions.

        Args:
            stock_id: Stock ID

        Returns:
            True if deleted, False if not found
        """
        return self.db.delete_stock(stock_id)

    # ========== Transaction Operations ==========

    def get_stock_transactions(self, stock_id: int) -> list[Transaction]:
        """Get all transactions for a stock.

        Args:
            stock_id: Stock ID

        Returns:
            List of transactions ordered by date (newest first)
        """
        return self.db.get_transactions_by_stock(stock_id)

    # ========== Utility Methods ==========

    def get_earliest_purchase_date(self, portfolio_id: int) -> Optional[date]:
        """Get earliest purchase date across all stocks in portfolio.

        Used to determine the start date for portfolio charts.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            Earliest purchase date or None if portfolio has no stocks
        """
        stocks = self.db.get_stocks_by_portfolio(portfolio_id)
        if not stocks:
            return None

        return min(stock.purchase_date for stock in stocks)
