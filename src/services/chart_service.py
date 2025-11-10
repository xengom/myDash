"""Chart data service for stock and portfolio visualization."""

from datetime import datetime, timedelta
from typing import Optional
import yfinance as yf
import pandas as pd


class ChartService:
    """Service for fetching and processing chart data."""

    def __init__(self):
        """Initialize chart service."""
        self._cache = {}
        self._cache_duration = timedelta(minutes=5)

    def get_stock_history(
        self,
        symbol: str,
        period: str = "3mo"
    ) -> Optional[pd.DataFrame]:
        """
        Get historical stock data.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Time period ('1mo', '3mo', '6mo', '1y')

        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        cache_key = f"{symbol}_{period}"

        # Check cache
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if datetime.now() - cached_time < self._cache_duration:
                return cached_data

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty:
                return None

            # Cache the result
            self._cache[cache_key] = (datetime.now(), hist)
            return hist

        except Exception as e:
            print(f"Error fetching history for {symbol}: {e}")
            return None

    def get_stock_returns(
        self,
        symbol: str,
        avg_price: float,
        period: str = "3mo"
    ) -> Optional[pd.DataFrame]:
        """
        Calculate stock returns vs average purchase price.

        Args:
            symbol: Stock symbol
            avg_price: Average purchase price
            period: Time period

        Returns:
            DataFrame with Date and Return % columns
        """
        hist = self.get_stock_history(symbol, period)
        if hist is None:
            return None

        # Calculate returns
        returns = pd.DataFrame()
        returns['Date'] = hist.index
        returns['Return%'] = ((hist['Close'] - avg_price) / avg_price * 100).values

        return returns

    def format_price_data(self, hist: pd.DataFrame) -> tuple[list[int], list[float]]:
        """
        Format price history for plotting.

        Args:
            hist: Historical data DataFrame

        Returns:
            Tuple of (indices, prices) - using numeric indices instead of date strings
        """
        if hist is None or hist.empty:
            return [], []

        # Use numeric indices instead of date strings to avoid plotext date parsing issues
        indices = list(range(len(hist)))
        prices = hist['Close'].values.tolist()

        return indices, prices

    def format_volume_data(self, hist: pd.DataFrame) -> tuple[list[str], list[float]]:
        """
        Format volume data for plotting.

        Args:
            hist: Historical data DataFrame

        Returns:
            Tuple of (dates, volumes)
        """
        if hist is None or hist.empty:
            return [], []

        dates = [d.strftime('%m/%d') for d in hist.index]
        volumes = hist['Volume'].values.tolist()

        return dates, volumes

    def get_portfolio_allocation(
        self,
        stocks: list[tuple[str, float, float]]
    ) -> tuple[list[str], list[float]]:
        """
        Calculate portfolio allocation percentages.

        Args:
            stocks: List of (symbol, quantity, current_price) tuples

        Returns:
            Tuple of (symbols, percentages)
        """
        if not stocks:
            return [], []

        # Calculate total value
        total_value = sum(qty * price for _, qty, price in stocks)

        if total_value == 0:
            return [], []

        # Calculate percentages
        symbols = [s[0] for s in stocks]
        percentages = [(qty * price / total_value * 100) for _, qty, price in stocks]

        return symbols, percentages

    def get_portfolio_performance(
        self,
        stocks: list[tuple[str, float, float, float]]
    ) -> tuple[list[str], list[float]]:
        """
        Calculate individual stock performance.

        Args:
            stocks: List of (symbol, quantity, avg_price, current_price) tuples

        Returns:
            Tuple of (symbols, return_percentages)
        """
        if not stocks:
            return [], []

        symbols = [s[0] for s in stocks]
        returns = [
            ((current - avg) / avg * 100) if avg > 0 else 0
            for _, _, avg, current in stocks
        ]

        return symbols, returns
