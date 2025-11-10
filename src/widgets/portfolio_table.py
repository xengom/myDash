"""Portfolio table widget with real-time stock data."""

from textual.app import ComposeResult
from textual.widgets import DataTable, Static
from textual.containers import Container, Vertical
from textual.reactive import reactive

from src.services import PortfolioManager, StockService


class PortfolioTable(Vertical):
    """Portfolio table widget showing stocks with real-time prices."""

    portfolio_id: reactive[int | None] = reactive(None)

    def __init__(self, portfolio_id: int | None = None):
        """Initialize portfolio table.

        Args:
            portfolio_id: Portfolio ID to display
        """
        super().__init__()
        self.portfolio_id = portfolio_id
        self.pm = PortfolioManager()
        self.stock_service = StockService()

    def compose(self) -> ComposeResult:
        """Compose the widget layout."""
        yield Static("📈 Portfolio", classes="panel-title")
        yield DataTable(id="portfolio-table")
        yield Static("", id="portfolio-summary")

    def on_mount(self) -> None:
        """Setup table when widget is mounted."""
        table = self.query_one("#portfolio-table", DataTable)

        # Add columns with wider widths for KRW display (₩ symbol can cause overlap)
        table.add_column("Symbol", width=14)
        table.add_column("Quantity", width=12)
        table.add_column("Avg Price", width=18)
        table.add_column("Current", width=18)
        table.add_column("Value", width=20)
        table.add_column("Cost", width=20)
        table.add_column("Gain/Loss", width=20)
        table.add_column("Gain %", width=14)

        # Set cursor type
        table.cursor_type = "row"

        # Load data if portfolio_id is set
        if self.portfolio_id:
            self.refresh_data()

    def watch_portfolio_id(self, new_id: int | None) -> None:
        """Watch for portfolio_id changes.

        Args:
            new_id: New portfolio ID
        """
        if new_id is not None:
            self.refresh_data()

    def refresh_data(self) -> None:
        """Refresh table data from database and stock service."""
        if not self.portfolio_id:
            return

        table = self.query_one("#portfolio-table", DataTable)
        table.clear()

        # Get stocks from database
        stocks = self.pm.get_stocks(self.portfolio_id)

        if not stocks:
            table.add_row("No stocks in portfolio", "", "", "", "", "", "", "")
            self._update_summary(0, 0, 0)
            return

        # Fetch current prices for all stocks
        symbols = [stock.symbol for stock in stocks]
        current_prices = self.stock_service.get_multiple_prices(symbols)

        # Get exchange rate for KRW conversion
        usd_to_krw = self.stock_service.get_usd_to_krw_rate()

        total_value_usd = 0
        total_cost_usd = 0
        total_gain_usd = 0

        # Add rows for each stock
        for stock in stocks:
            current_price = current_prices.get(stock.symbol)

            if current_price:
                is_korean = self.stock_service.is_korean_stock(stock.symbol)

                value = stock.quantity * current_price
                cost = stock.quantity * stock.avg_price
                gain = value - cost
                gain_pct = (gain / cost * 100) if cost > 0 else 0

                # Convert to USD for total calculation
                if is_korean and usd_to_krw:
                    value_usd = value / usd_to_krw
                    cost_usd = cost / usd_to_krw
                    gain_usd = gain / usd_to_krw
                else:
                    value_usd = value
                    cost_usd = cost
                    gain_usd = gain

                total_value_usd += value_usd
                total_cost_usd += cost_usd
                total_gain_usd += gain_usd

                # Format values with appropriate currency (add space after ₩ for better visibility)
                if is_korean:
                    avg_price_str = f"₩ {stock.avg_price:,.0f}"
                    current_price_str = f"₩ {current_price:,.0f}"
                    value_str = f"₩ {value:,.0f}"
                    cost_str = f"₩ {cost:,.0f}"
                    # Color code gain/loss
                    if gain >= 0:
                        gain_str = f"[green]₩ {gain:+,.0f}[/green]"
                    else:
                        gain_str = f"[red]₩ {gain:+,.0f}[/red]"
                else:
                    avg_price_str = f"${stock.avg_price:.2f}"
                    current_price_str = f"${current_price:.2f}"
                    value_str = f"${value:,.2f}"
                    cost_str = f"${cost:,.2f}"
                    # Color code gain/loss
                    if gain >= 0:
                        gain_str = f"[green]${gain:+,.2f}[/green]"
                    else:
                        gain_str = f"[red]${gain:+,.2f}[/red]"

                # Color code gain percentage
                if gain >= 0:
                    gain_pct_str = f"[green]{gain_pct:+.2f}%[/green]"
                else:
                    gain_pct_str = f"[red]{gain_pct:+.2f}%[/red]"

                table.add_row(
                    stock.symbol,
                    f"{stock.quantity:.2f}",
                    avg_price_str,
                    current_price_str,
                    value_str,
                    cost_str,
                    gain_str,
                    gain_pct_str
                )
            else:
                # Price fetch failed
                is_korean = self.stock_service.is_korean_stock(stock.symbol)
                cost = stock.quantity * stock.avg_price

                # Convert to USD for total
                if is_korean and usd_to_krw:
                    cost_usd = cost / usd_to_krw
                else:
                    cost_usd = cost

                total_cost_usd += cost_usd

                # Format with appropriate currency
                if is_korean:
                    avg_price_str = f"₩ {stock.avg_price:,.0f}"
                    cost_str = f"₩ {cost:,.0f}"
                else:
                    avg_price_str = f"${stock.avg_price:.2f}"
                    cost_str = f"${cost:,.2f}"

                table.add_row(
                    stock.symbol,
                    f"{stock.quantity:.2f}",
                    avg_price_str,
                    "[dim]N/A[/dim]",
                    "[dim]N/A[/dim]",
                    cost_str,
                    "[dim]N/A[/dim]",
                    "[dim]N/A[/dim]"
                )

        # Update summary with KRW converted values
        if usd_to_krw:
            total_value_krw = total_value_usd * usd_to_krw
            total_cost_krw = total_cost_usd * usd_to_krw
            total_gain_krw = total_gain_usd * usd_to_krw
            self._update_summary(total_value_krw, total_cost_krw, total_gain_krw, use_krw=True)
        else:
            self._update_summary(total_value_usd, total_cost_usd, total_gain_usd, use_krw=False)

    def _update_summary(self, total_value: float, total_cost: float, total_gain: float, use_krw: bool = False) -> None:
        """Update portfolio summary display.

        Args:
            total_value: Total current value
            total_cost: Total cost basis
            total_gain: Total gain/loss
            use_krw: Whether to display in KRW
        """
        summary = self.query_one("#portfolio-summary", Static)

        if total_cost == 0:
            summary.update("")
            return

        gain_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0

        # Format with appropriate currency and shorter labels for space
        if use_krw:
            value_str = f"₩ {total_value:,.0f}"
            cost_str = f"₩ {total_cost:,.0f}"
            if total_gain >= 0:
                gain_str = f"[green]₩ {total_gain:+,.0f}[/green]"
            else:
                gain_str = f"[red]₩ {total_gain:+,.0f}[/red]"
        else:
            value_str = f"${total_value:,.2f}"
            cost_str = f"${total_cost:,.2f}"
            if total_gain >= 0:
                gain_str = f"[green]${total_gain:+,.2f}[/green]"
            else:
                gain_str = f"[red]${total_gain:+,.2f}[/red]"

        # Shorter summary format to accommodate large KRW values
        pct_color = "green" if gain_pct >= 0 else "red"
        summary_text = (
            f"💰 {value_str} | "
            f"📊 {cost_str} | "
            f"📈 {gain_str} [{pct_color}]({gain_pct:+.2f}%)[/{pct_color}]"
        )

        summary.update(summary_text)

    def get_selected_stock_symbol(self) -> str | None:
        """Get the symbol of the currently selected stock.

        Returns:
            Stock symbol or None if nothing selected
        """
        table = self.query_one("#portfolio-table", DataTable)

        if table.cursor_row < 0 or table.cursor_row >= table.row_count:
            return None

        # Get row key and extract symbol (first column)
        try:
            # Iterate through rows to find the row at cursor position
            for idx, row_key in enumerate(table.rows):
                if idx == table.cursor_row:
                    # Get the row data
                    row_data = table.get_row(row_key)
                    if row_data and len(row_data) > 0:
                        return str(row_data[0])
                    break
        except Exception:
            return None

        return None
