"""Chart visualization widgets using plotext."""

from textual.widgets import Static
from textual.reactive import reactive
from rich.console import RenderableType
from rich.text import Text
import plotext as plt

from src.services.chart_service import ChartService
from src.services import StockService


class ChartView(Static):
    """Detail chart view for stocks and portfolio."""

    view_mode = reactive("stock")  # "stock" or "portfolio"
    selected_symbol = reactive("")
    selected_data = reactive(None)

    def __init__(self, **kwargs):
        """Initialize chart view."""
        super().__init__(**kwargs)
        self.chart_service = ChartService()
        self.stock_service = StockService()

    def render(self) -> RenderableType:
        """Render the chart."""
        if self.view_mode == "stock" and self.selected_symbol:
            return self._render_stock_chart()
        elif self.view_mode == "portfolio" and self.selected_data:
            return self._render_portfolio_chart()
        else:
            return Text("📊 차트를 보려면 주식을 선택하거나 'v' 키를 누르세요", style="dim italic")

    def _render_stock_chart(self) -> RenderableType:
        """Render stock detail chart."""
        if not self.selected_symbol or not self.selected_data:
            return "No data"

        symbol = self.selected_symbol
        avg_price = self.selected_data.get('avg_price', 0)
        quantity = self.selected_data.get('quantity', 0)

        # Fetch historical data
        hist = self.chart_service.get_stock_history(symbol, period="3mo")
        if hist is None or hist.empty:
            return f"📉 {symbol} 차트 데이터를 가져올 수 없습니다"

        # Get current price
        current_price = self.stock_service.get_current_price(symbol)
        if current_price is None:
            current_price = hist['Close'].iloc[-1]

        # Format data
        indices, prices = self.chart_service.format_price_data(hist)

        # Get date labels for display
        date_labels = [hist.index[i].strftime('%m/%d') for i in range(0, len(hist), max(1, len(hist) // 10))]

        # Create chart using plotext with dynamic width
        plt.clf()
        plt.theme('dark')

        # Get terminal width dynamically
        try:
            import shutil
            term_width = shutil.get_terminal_size().columns
            chart_width = max(80, term_width - 10)  # Use terminal width minus padding
        except:
            chart_width = 80  # Fallback to 80

        plt.plot_size(chart_width, 15)

        # Price chart
        plt.plot(indices, prices, marker="•", label=f"{symbol} Price")

        # Add average price line
        if avg_price > 0:
            plt.hline(avg_price, "red")

        # Check if Korean stock for currency formatting
        is_korean = self.stock_service.is_korean_stock(symbol)
        currency_label = "KRW" if is_korean else "USD"

        plt.title(f"📈 {symbol} - 3 Month Price History")
        plt.xlabel("Days")
        plt.ylabel(f"Price ({currency_label})")

        # Show x-axis labels with date annotations
        step = max(1, len(indices) // 10)
        tick_positions = [indices[i] for i in range(0, len(indices), step)]
        plt.xticks(tick_positions, date_labels)

        plt.grid(True, True)

        chart_output = plt.build()

        # Add summary stats with appropriate currency
        return_pct = ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0
        total_value = quantity * current_price
        total_gain = quantity * (current_price - avg_price)

        if is_korean:
            current_str = f"₩{current_price:,.0f}"
            avg_str = f"₩{avg_price:,.0f}"
            value_str = f"₩{total_value:,.0f}"
            gain_str = f"₩{total_gain:+,.0f}"
        else:
            current_str = f"${current_price:.2f}"
            avg_str = f"${avg_price:.2f}"
            value_str = f"${total_value:,.2f}"
            gain_str = f"${total_gain:+,.2f}"

        summary = f"\n💰 Current: {current_str} | 📊 Avg: {avg_str} | "
        summary += f"{'📈' if return_pct >= 0 else '📉'} {return_pct:+.2f}% | "
        summary += f"💵 Value: {value_str} | "
        summary += f"{'✅' if total_gain >= 0 else '❌'} P/L: {gain_str}"

        return Text.from_ansi(chart_output + summary)

    def _render_portfolio_chart(self) -> RenderableType:
        """Render portfolio summary chart."""
        if not self.selected_data:
            return "No portfolio data"

        stocks = self.selected_data

        if not stocks:
            return "📊 포트폴리오가 비어있습니다"

        # Get exchange rate for KRW conversion
        usd_to_krw = self.stock_service.get_usd_to_krw_rate()

        # Prepare data for allocation chart
        stock_data = []
        total_value_usd = 0
        total_gain_usd = 0

        for stock in stocks:
            symbol = stock['symbol']
            quantity = stock['quantity']
            avg_price = stock['avg_price']
            current_price = self.stock_service.get_current_price(symbol)

            if current_price is None:
                continue

            is_korean = self.stock_service.is_korean_stock(symbol)
            value = quantity * current_price
            gain = quantity * (current_price - avg_price)

            # Convert to USD for chart consistency
            if is_korean and usd_to_krw:
                value_usd = value / usd_to_krw
                gain_usd = gain / usd_to_krw
            else:
                value_usd = value
                gain_usd = gain

            stock_data.append({
                'symbol': symbol,
                'value': value_usd,
                'gain': gain_usd,
                'return_pct': ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0
            })

            total_value_usd += value_usd
            total_gain_usd += gain_usd

        if not stock_data:
            return "📉 주식 데이터를 가져올 수 없습니다"

        # Get terminal width dynamically
        try:
            import shutil
            term_width = shutil.get_terminal_size().columns
            chart_width = max(80, term_width - 10)  # Use terminal width minus padding
        except:
            chart_width = 80  # Fallback to 80

        # Create allocation bar chart
        plt.clf()
        plt.theme('dark')
        plt.plot_size(chart_width, 15)

        symbols = [s['symbol'] for s in stock_data]
        values = [s['value'] for s in stock_data]

        plt.bar(symbols, values, marker="●", orientation="v")
        plt.title("📊 Portfolio Allocation by Value")
        plt.xlabel("Stock")
        plt.ylabel("Value (USD equiv.)")
        plt.grid(False, True)

        chart_output = plt.build()

        # Add performance chart
        plt.clf()
        plt.theme('dark')
        plt.plot_size(chart_width, 12)

        returns = [s['return_pct'] for s in stock_data]
        colors = ['green' if r >= 0 else 'red' for r in returns]

        plt.bar(symbols, returns, marker="●", orientation="v")
        plt.hline(0, "white")
        plt.title("📈 Stock Performance (%)")
        plt.xlabel("Stock")
        plt.ylabel("Return (%)")
        plt.grid(False, True)

        chart_output2 = plt.build()

        # Add summary with KRW conversion
        total_return = (total_gain_usd / (total_value_usd - total_gain_usd) * 100) if (total_value_usd - total_gain_usd) > 0 else 0

        if usd_to_krw:
            total_value_krw = total_value_usd * usd_to_krw
            total_gain_krw = total_gain_usd * usd_to_krw
            summary = f"\n💰 Total Value: ₩{total_value_krw:,.0f} | "
            summary += f"{'📈' if total_return >= 0 else '📉'} Return: {total_return:+.2f}% | "
            summary += f"{'✅' if total_gain_krw >= 0 else '❌'} P/L: ₩{total_gain_krw:+,.0f}"
        else:
            summary = f"\n💰 Total Value: ${total_value_usd:,.2f} | "
            summary += f"{'📈' if total_return >= 0 else '📉'} Return: {total_return:+.2f}% | "
            summary += f"{'✅' if total_gain_usd >= 0 else '❌'} P/L: ${total_gain_usd:+,.2f}"

        return Text.from_ansi(chart_output + "\n" + chart_output2 + summary)

    def show_stock_chart(self, symbol: str, data: dict):
        """
        Show chart for a specific stock.

        Args:
            symbol: Stock symbol
            data: Dict with 'avg_price' and 'quantity'
        """
        self.view_mode = "stock"
        self.selected_symbol = symbol
        self.selected_data = data
        self.refresh()

    def show_portfolio_chart(self, stocks: list[dict]):
        """
        Show portfolio summary chart.

        Args:
            stocks: List of stock dicts with symbol, quantity, avg_price
        """
        self.view_mode = "portfolio"
        self.selected_data = stocks
        self.refresh()

    def hide_chart(self):
        """Hide the chart view."""
        self.view_mode = ""
        self.selected_symbol = ""
        self.selected_data = None
        self.refresh()
