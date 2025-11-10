"""Database schema migrations."""

import sqlite3
from pathlib import Path


def create_schema(db_path: str) -> None:
    """Create database schema.

    Args:
        db_path: Path to SQLite database file
    """
    # Ensure data directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create portfolios table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create stocks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                purchase_date DATE NOT NULL,
                quantity REAL NOT NULL CHECK(quantity > 0),
                avg_price REAL NOT NULL CHECK(avg_price > 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
                UNIQUE(portfolio_id, symbol)
            )
        """)

        # Create transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_id INTEGER NOT NULL,
                txn_type TEXT NOT NULL CHECK(txn_type IN ('BUY', 'SELL')),
                quantity REAL NOT NULL CHECK(quantity > 0),
                price REAL NOT NULL CHECK(price > 0),
                txn_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for better query performance
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_portfolios_name ON portfolios(name)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_stocks_portfolio ON stocks(portfolio_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_stocks_purchase_date ON stocks(purchase_date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_stock ON transactions(stock_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(txn_date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(txn_type)"
        )

        conn.commit()
        print(f"✓ Database schema created successfully")
        print(f"✓ Location: {db_path}")

    except sqlite3.Error as e:
        print(f"✗ Error creating schema: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_schema(db_path: str) -> bool:
    """Verify database schema exists and is correct.

    Args:
        db_path: Path to SQLite database file

    Returns:
        True if schema is valid, False otherwise
    """
    if not Path(db_path).exists():
        print(f"✗ Database file not found: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('portfolios', 'stocks', 'transactions')
        """)
        tables = [row[0] for row in cursor.fetchall()]

        if len(tables) != 3:
            print(f"✗ Expected 3 tables, found {len(tables)}: {tables}")
            return False

        print(f"✓ All tables exist: {', '.join(tables)}")

        # Check indexes exist
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_%'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"✓ Found {len(indexes)} indexes")

        return True

    except sqlite3.Error as e:
        print(f"✗ Error verifying schema: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    from src.config.settings import settings

    print("=" * 60)
    print("Database Migration - Creating Schema")
    print("=" * 60)

    create_schema(settings.DATABASE_PATH)

    print("\n" + "=" * 60)
    print("Verifying Schema")
    print("=" * 60)

    if verify_schema(settings.DATABASE_PATH):
        print("\n✓ Database setup complete!")
    else:
        print("\n✗ Database verification failed")
        exit(1)
