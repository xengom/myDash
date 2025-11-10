"""Stock market data service using yfinance."""

from datetime import datetime, timedelta
from typing import Optional
import yfinance as yf
import pandas as pd


class StockService:
    """Fetches real-time and historical stock data using yfinance."""

    def __init__(self):
        """Initialize stock service with cache."""
        self._cache = {}
        self._cache_duration = timedelta(minutes=5)
        self._exchange_rate_cache = None
        self._exchange_rate_time = None

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current stock price.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOG')

        Returns:
            Current price or None if fetch fails
        """
        # Check cache
        cache_key = f"price_{symbol}"
        if cache_key in self._cache:
            cached_time, cached_price = self._cache[cache_key]
            if datetime.now() - cached_time < self._cache_duration:
                return cached_price

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Try multiple price fields in order of preference
            price = (
                info.get('currentPrice') or
                info.get('regularMarketPrice') or
                info.get('previousClose')
            )

            if price:
                self._cache[cache_key] = (datetime.now(), price)
                return float(price)

        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None

        return None

    def get_multiple_prices(self, symbols: list[str]) -> dict[str, Optional[float]]:
        """Get current prices for multiple stocks efficiently.

        Args:
            symbols: List of stock ticker symbols

        Returns:
            Dictionary mapping symbol to current price
        """
        prices = {}

        for symbol in symbols:
            prices[symbol] = self.get_current_price(symbol)

        return prices

    def get_stock_history(
        self,
        symbol: str,
        time_range: str = "1mo"
    ) -> Optional[pd.DataFrame]:
        """Get historical stock data for charts.

        Args:
            symbol: Stock ticker symbol
            time_range: Time range ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'ytd', 'max')

        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
            or None if fetch fails
        """
        try:
            ticker = yf.Ticker(symbol)

            # Map time ranges to yfinance periods
            period_map = {
                "1d": "1d",
                "5d": "5d",
                "1mo": "1mo",
                "3mo": "3mo",
                "6mo": "6mo",
                "1y": "1y",
                "2y": "2y",
                "5y": "5y",
                "ytd": "ytd",
                "max": "max"
            }

            period = period_map.get(time_range, "1mo")
            history = ticker.history(period=period)

            if history.empty:
                return None

            return history

        except Exception as e:
            print(f"Error fetching history for {symbol}: {e}")
            return None

    def get_stock_info(self, symbol: str) -> Optional[dict]:
        """Get detailed stock information.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with stock info or None if fetch fails
        """
        # Check cache
        cache_key = f"info_{symbol}"
        if cache_key in self._cache:
            cached_time, cached_info = self._cache[cache_key]
            if datetime.now() - cached_time < self._cache_duration:
                return cached_info

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Extract relevant fields
            stock_info = {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "current_price": (
                    info.get("currentPrice") or
                    info.get("regularMarketPrice") or
                    info.get("previousClose")
                ),
                "previous_close": info.get("previousClose"),
                "open": info.get("open"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "volume": info.get("volume"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "52w_high": info.get("fiftyTwoWeekHigh"),
                "52w_low": info.get("fiftyTwoWeekLow"),
            }

            self._cache[cache_key] = (datetime.now(), stock_info)
            return stock_info

        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return None

    def is_korean_stock(self, symbol: str) -> bool:
        """Check if stock is a Korean stock.

        Args:
            symbol: Stock ticker symbol

        Returns:
            True if symbol ends with .KS or .KQ
        """
        return symbol.endswith('.KS') or symbol.endswith('.KQ')

    def get_usd_to_krw_rate(self) -> Optional[float]:
        """Get current USD to KRW exchange rate.

        Returns:
            Exchange rate (KRW per 1 USD) or None if fetch fails
        """
        # Check cache (10 minute cache for exchange rate)
        if self._exchange_rate_cache and self._exchange_rate_time:
            if datetime.now() - self._exchange_rate_time < timedelta(minutes=10):
                return self._exchange_rate_cache

        try:
            ticker = yf.Ticker("KRW=X")
            info = ticker.info

            rate = (
                info.get('regularMarketPrice') or
                info.get('previousClose')
            )

            if rate:
                self._exchange_rate_cache = float(rate)
                self._exchange_rate_time = datetime.now()
                return float(rate)

        except Exception as e:
            print(f"Error fetching KRW exchange rate: {e}")
            return None

        return None

    def format_currency(self, amount: float, symbol: str) -> str:
        """Format currency based on stock origin.

        Args:
            amount: Amount to format
            symbol: Stock ticker symbol

        Returns:
            Formatted currency string
        """
        if self.is_korean_stock(symbol):
            return f"₩{amount:,.0f}"
        else:
            return f"${amount:,.2f}"

    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        self._exchange_rate_cache = None
        self._exchange_rate_time = None

    def get_cache_stats(self) -> dict:
        """Get cache statistics for debugging.

        Returns:
            Dictionary with cache size and oldest entry time
        """
        if not self._cache:
            return {"size": 0, "oldest_entry": None}

        oldest_time = min(time for time, _ in self._cache.values())

        return {
            "size": len(self._cache),
            "oldest_entry": oldest_time,
            "cache_duration_minutes": self._cache_duration.total_seconds() / 60
        }
