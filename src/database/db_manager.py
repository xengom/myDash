"""Database manager for SQLite operations."""

import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import Optional

from src.models import Portfolio, Stock, Transaction, TransactionType
from src.config.settings import settings


class DatabaseManager:
    """Manages SQLite database operations."""

    def __init__(self, db_path: str | None = None):
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database file (default: from settings)
        """
        self.db_path = db_path or settings.DATABASE_PATH
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Ensure database file and schema exist."""
        if not Path(self.db_path).exists():
            from src.database.migrations import create_schema
            create_schema(self.db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory.

        Returns:
            Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ========== Portfolio Operations ==========

    def create_portfolio(self, name: str) -> Portfolio:
        """Create a new portfolio.

        Args:
            name: Portfolio name

        Returns:
            Created portfolio

        Raises:
            sqlite3.IntegrityError: If portfolio name already exists
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO portfolios (name) VALUES (?)",
                (name,)
            )
            conn.commit()

            portfolio_id = cursor.lastrowid
            return self.get_portfolio(portfolio_id)

        finally:
            conn.close()

    def get_portfolio(self, portfolio_id: int) -> Optional[Portfolio]:
        """Get portfolio by ID.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            Portfolio or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM portfolios WHERE id = ?",
                (portfolio_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            return Portfolio(
                id=row['id'],
                name=row['name'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )

        finally:
            conn.close()

    def get_all_portfolios(self) -> list[Portfolio]:
        """Get all portfolios.

        Returns:
            List of portfolios
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM portfolios ORDER BY name")
            rows = cursor.fetchall()

            return [
                Portfolio(
                    id=row['id'],
                    name=row['name'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                for row in rows
            ]

        finally:
            conn.close()

    def update_portfolio(self, portfolio_id: int, name: str) -> Optional[Portfolio]:
        """Update portfolio name.

        Args:
            portfolio_id: Portfolio ID
            name: New portfolio name

        Returns:
            Updated portfolio or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """UPDATE portfolios
                   SET name = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (name, portfolio_id)
            )
            conn.commit()

            if cursor.rowcount == 0:
                return None

            return self.get_portfolio(portfolio_id)

        finally:
            conn.close()

    def delete_portfolio(self, portfolio_id: int) -> bool:
        """Delete portfolio and all associated stocks.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            True if deleted, False if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM portfolios WHERE id = ?", (portfolio_id,))
            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    # ========== Stock Operations ==========

    def create_stock(
        self,
        portfolio_id: int,
        symbol: str,
        quantity: float,
        avg_price: float,
        purchase_date: date
    ) -> Stock:
        """Create a new stock.

        Args:
            portfolio_id: Portfolio ID
            symbol: Stock ticker symbol
            quantity: Number of shares
            avg_price: Average purchase price
            purchase_date: Purchase date

        Returns:
            Created stock
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO stocks (portfolio_id, symbol, quantity, avg_price, purchase_date)
                   VALUES (?, ?, ?, ?, ?)""",
                (portfolio_id, symbol.upper(), quantity, avg_price, purchase_date.isoformat())
            )
            conn.commit()

            stock_id = cursor.lastrowid
            return self.get_stock(stock_id)

        finally:
            conn.close()

    def get_stock(self, stock_id: int) -> Optional[Stock]:
        """Get stock by ID.

        Args:
            stock_id: Stock ID

        Returns:
            Stock or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM stocks WHERE id = ?", (stock_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return Stock(
                id=row['id'],
                portfolio_id=row['portfolio_id'],
                symbol=row['symbol'],
                quantity=row['quantity'],
                avg_price=row['avg_price'],
                purchase_date=date.fromisoformat(row['purchase_date']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )

        finally:
            conn.close()

    def get_stock_by_symbol(self, portfolio_id: int, symbol: str) -> Optional[Stock]:
        """Get stock by portfolio ID and symbol.

        Args:
            portfolio_id: Portfolio ID
            symbol: Stock ticker symbol

        Returns:
            Stock or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM stocks WHERE portfolio_id = ? AND symbol = ?",
                (portfolio_id, symbol.upper())
            )
            row = cursor.fetchone()

            if not row:
                return None

            return Stock(
                id=row['id'],
                portfolio_id=row['portfolio_id'],
                symbol=row['symbol'],
                quantity=row['quantity'],
                avg_price=row['avg_price'],
                purchase_date=date.fromisoformat(row['purchase_date']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )

        finally:
            conn.close()

    def get_stocks_by_portfolio(self, portfolio_id: int) -> list[Stock]:
        """Get all stocks in a portfolio.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            List of stocks
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM stocks WHERE portfolio_id = ? ORDER BY symbol",
                (portfolio_id,)
            )
            rows = cursor.fetchall()

            return [
                Stock(
                    id=row['id'],
                    portfolio_id=row['portfolio_id'],
                    symbol=row['symbol'],
                    quantity=row['quantity'],
                    avg_price=row['avg_price'],
                    purchase_date=date.fromisoformat(row['purchase_date']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                for row in rows
            ]

        finally:
            conn.close()

    def update_stock(
        self,
        stock_id: int,
        quantity: Optional[float] = None,
        avg_price: Optional[float] = None,
        purchase_date: Optional[date] = None
    ) -> Optional[Stock]:
        """Update stock details.

        Args:
            stock_id: Stock ID
            quantity: New quantity (optional)
            avg_price: New average price (optional)
            purchase_date: New purchase date (optional)

        Returns:
            Updated stock or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Build dynamic UPDATE query
            updates = []
            params = []

            if quantity is not None:
                updates.append("quantity = ?")
                params.append(quantity)

            if avg_price is not None:
                updates.append("avg_price = ?")
                params.append(avg_price)

            if purchase_date is not None:
                updates.append("purchase_date = ?")
                params.append(purchase_date.isoformat())

            if not updates:
                return self.get_stock(stock_id)

            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(stock_id)

            query = f"UPDATE stocks SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()

            if cursor.rowcount == 0:
                return None

            return self.get_stock(stock_id)

        finally:
            conn.close()

    def delete_stock(self, stock_id: int) -> bool:
        """Delete stock and all associated transactions.

        Args:
            stock_id: Stock ID

        Returns:
            True if deleted, False if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM stocks WHERE id = ?", (stock_id,))
            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    # ========== Transaction Operations ==========

    def create_transaction(
        self,
        stock_id: int,
        txn_type: TransactionType,
        quantity: float,
        price: float,
        txn_date: date
    ) -> Transaction:
        """Create a new transaction.

        Args:
            stock_id: Stock ID
            txn_type: Transaction type (BUY or SELL)
            quantity: Number of shares
            price: Price per share
            txn_date: Transaction date

        Returns:
            Created transaction
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO transactions (stock_id, txn_type, quantity, price, txn_date)
                   VALUES (?, ?, ?, ?, ?)""",
                (stock_id, txn_type.value, quantity, price, txn_date.isoformat())
            )
            conn.commit()

            transaction_id = cursor.lastrowid
            return self.get_transaction(transaction_id)

        finally:
            conn.close()

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return Transaction(
                id=row['id'],
                stock_id=row['stock_id'],
                txn_type=TransactionType(row['txn_type']),
                quantity=row['quantity'],
                price=row['price'],
                txn_date=date.fromisoformat(row['txn_date']),
                created_at=datetime.fromisoformat(row['created_at'])
            )

        finally:
            conn.close()

    def get_transactions_by_stock(self, stock_id: int) -> list[Transaction]:
        """Get all transactions for a stock.

        Args:
            stock_id: Stock ID

        Returns:
            List of transactions ordered by date (newest first)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM transactions WHERE stock_id = ? ORDER BY txn_date DESC",
                (stock_id,)
            )
            rows = cursor.fetchall()

            return [
                Transaction(
                    id=row['id'],
                    stock_id=row['stock_id'],
                    txn_type=TransactionType(row['txn_type']),
                    quantity=row['quantity'],
                    price=row['price'],
                    txn_date=date.fromisoformat(row['txn_date']),
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                for row in rows
            ]

        finally:
            conn.close()
