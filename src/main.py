"""myDash - Personal Dashboard TUI Application."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container, Vertical

from src.config.settings import settings
from src.widgets import (
    PortfolioTable,
    AddStockModal,
    EditStockModal,
    DeleteConfirmModal,
    GooglePanel,
    ChartView,
)
from src.services import PortfolioManager, SystemService, WeatherService


class HeaderBar(Static):
    """System status header bar."""

    def __init__(self):
        """Initialize header bar."""
        super().__init__()
        self.system_service = SystemService()
        self.weather_service = WeatherService()

    def on_mount(self) -> None:
        """Initialize header content and start update timer."""
        self.update_status()
        self.set_interval(1.0, self.update_status)

    def update_status(self) -> None:
        """Update header with current system status."""
        # System info
        sys_status = self.system_service.format_status_line()

        # Weather info
        weather_status = self.weather_service.format_weather_short(city=settings.WEATHER_CITY)

        # Combined status
        status = f"myDash | {sys_status} | {weather_status}"
        self.update(status)


class MyDashApp(App):
    """myDash TUI application."""

    CSS = """
    HeaderBar {
        dock: top;
        height: 1;
        background: $primary;
        color: $text;
    }

    #main-container {
        layout: horizontal;
        height: 3fr;
    }

    .panel {
        border: solid $primary;
        height: 100%;
        padding: 1;
    }

    .panel-title {
        text-style: bold;
        background: $primary;
        padding: 0 1;
        margin-bottom: 1;
    }

    #stock-panel {
        width: 60%;
    }

    #google-panel {
        width: 40%;
    }

    #portfolio-table {
        height: 1fr;
    }

    #portfolio-summary {
        dock: bottom;
        height: 2;
        background: $surface;
        padding: 0 2;
        content-align: center middle;
    }

    #chart-container {
        dock: bottom;
        height: 35;
        border: solid $primary;
        padding: 1;
        display: none;
    }

    #chart-container.visible {
        display: block;
    }

    #chart-view {
        height: 100%;
        width: 100%;
        overflow-y: auto;
        overflow-x: hidden;
    }
    """

    BINDINGS = [
        ("q", "quit", "종료"),
        ("r", "refresh", "새로고침"),
        ("a", "add_stock", "주식 추가"),
        ("e", "edit_stock", "주식 수정"),
        ("d", "delete_stock", "주식 삭제"),
        ("v", "toggle_stock_chart", "주식 차트"),
        ("ctrl+v", "toggle_portfolio_chart", "포트폴리오 차트"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield HeaderBar()
        yield Footer()
        with Container(id="main-container"):
            with Vertical(id="stock-panel", classes="panel"):
                yield PortfolioTable()
            with Vertical(id="google-panel", classes="panel"):
                yield GooglePanel()
        with Container(id="chart-container"):
            yield ChartView(id="chart-view")

    def on_mount(self) -> None:
        """Called when app starts."""
        self.title = "myDash"
        self.sub_title = f"Database: {settings.DATABASE_PATH}"

        # Initialize with test data if no portfolios exist
        pm = PortfolioManager()
        portfolios = pm.get_all_portfolios()

        if not portfolios:
            # Create default portfolio
            portfolio = pm.create_portfolio("My Portfolio")

        # Set first portfolio to display
        portfolios = pm.get_all_portfolios()
        if portfolios:
            portfolio_table = self.query_one(PortfolioTable)
            portfolio_table.portfolio_id = portfolios[0].id

    def action_refresh(self) -> None:
        """Refresh portfolio data."""
        portfolio_table = self.query_one(PortfolioTable)
        portfolio_table.refresh_data()
        self.notify("✅ 데이터 새로고침 완료", severity="information")

    def action_add_stock(self) -> None:
        """Add new stock."""
        portfolio_table = self.query_one(PortfolioTable)
        if not portfolio_table.portfolio_id:
            self.notify("❌ 먼저 포트폴리오를 선택하세요", severity="error")
            return

        self.push_screen(AddStockModal(portfolio_table.portfolio_id), callback=self._handle_add_stock)

    def _handle_add_stock(self, result) -> None:
        """Handle add stock result."""
        if result:
            pm = PortfolioManager()
            try:
                stock = pm.add_stock(
                    portfolio_id=result["portfolio_id"],
                    symbol=result["symbol"],
                    quantity=result["quantity"],
                    price=result["price"],
                    purchase_date=result["purchase_date"]
                )
                portfolio_table = self.query_one(PortfolioTable)
                portfolio_table.refresh_data()
                self.notify(
                    f"✅ {stock.symbol} 추가됨: {stock.quantity}주 @ ${stock.avg_price:.2f}",
                    severity="information"
                )
            except Exception as e:
                self.notify(f"❌ 오류: {str(e)}", severity="error")

    def action_edit_stock(self) -> None:
        """Edit selected stock."""
        portfolio_table = self.query_one(PortfolioTable)
        symbol = portfolio_table.get_selected_stock_symbol()

        if not symbol:
            self.notify("❌ 수정할 주식을 선택하세요", severity="error")
            return

        pm = PortfolioManager()
        stock = pm.db.get_stock_by_symbol(portfolio_table.portfolio_id, symbol)

        if not stock:
            self.notify("❌ 주식을 찾을 수 없습니다", severity="error")
            return

        self.push_screen(
            EditStockModal(stock.id, stock.symbol, stock.quantity, stock.avg_price),
            callback=self._handle_edit_stock
        )

    def _handle_edit_stock(self, result) -> None:
        """Handle edit stock result."""
        if result:
            pm = PortfolioManager()
            try:
                updated_stock = pm.update_stock(
                    stock_id=result["stock_id"],
                    quantity=result["quantity"],
                    avg_price=result["avg_price"]
                )
                portfolio_table = self.query_one(PortfolioTable)
                portfolio_table.refresh_data()
                self.notify(
                    f"✅ {updated_stock.symbol} 업데이트됨",
                    severity="information"
                )
            except Exception as e:
                self.notify(f"❌ 오류: {str(e)}", severity="error")

    def action_delete_stock(self) -> None:
        """Delete selected stock."""
        portfolio_table = self.query_one(PortfolioTable)
        symbol = portfolio_table.get_selected_stock_symbol()

        if not symbol:
            self.notify("❌ 삭제할 주식을 선택하세요", severity="error")
            return

        self.push_screen(DeleteConfirmModal(symbol), callback=lambda confirm: self._handle_delete_stock(symbol, confirm))

    def _handle_delete_stock(self, symbol: str, confirm: bool) -> None:
        """Handle delete stock confirmation."""
        if confirm:
            portfolio_table = self.query_one(PortfolioTable)
            pm = PortfolioManager()
            stock = pm.db.get_stock_by_symbol(portfolio_table.portfolio_id, symbol)

            if stock and pm.delete_stock(stock.id):
                portfolio_table.refresh_data()
                self.notify(f"✅ {symbol} 삭제됨", severity="information")
            else:
                self.notify("❌ 삭제 실패", severity="error")

    def action_toggle_stock_chart(self) -> None:
        """Toggle stock chart view visibility."""
        portfolio_table = self.query_one(PortfolioTable)
        symbol = portfolio_table.get_selected_stock_symbol()

        if not symbol:
            self.notify("❌ 주식을 선택하세요", severity="error")
            return

        chart_container = self.query_one("#chart-container")
        chart_view = self.query_one(ChartView)

        if chart_container.has_class("visible") and chart_view.view_mode == "stock":
            # Hide chart
            chart_container.remove_class("visible")
            chart_view.hide_chart()
            self.notify("📊 차트 숨김", severity="information")
        else:
            # Show stock chart
            self._show_stock_chart()

    def action_toggle_portfolio_chart(self) -> None:
        """Toggle portfolio chart view visibility."""
        chart_container = self.query_one("#chart-container")
        chart_view = self.query_one(ChartView)

        if chart_container.has_class("visible") and chart_view.view_mode == "portfolio":
            # Hide chart
            chart_container.remove_class("visible")
            chart_view.hide_chart()
            self.notify("📊 차트 숨김", severity="information")
        else:
            # Show portfolio chart
            self._show_portfolio_chart()

    def _show_stock_chart(self) -> None:
        """Show stock chart for selected stock."""
        portfolio_table = self.query_one(PortfolioTable)
        chart_container = self.query_one("#chart-container")
        chart_view = self.query_one(ChartView)

        symbol = portfolio_table.get_selected_stock_symbol()
        if not symbol:
            self.notify("❌ 주식을 선택하세요", severity="error")
            return

        pm = PortfolioManager()
        stock = pm.db.get_stock_by_symbol(portfolio_table.portfolio_id, symbol)

        if stock:
            chart_container.add_class("visible")
            chart_view.show_stock_chart(
                symbol,
                {
                    'avg_price': stock.avg_price,
                    'quantity': stock.quantity
                }
            )
            self.notify(f"📈 {symbol} 차트 표시", severity="information")
        else:
            self.notify("❌ 주식 정보를 찾을 수 없습니다", severity="error")

    def _show_portfolio_chart(self) -> None:
        """Show portfolio summary chart."""
        portfolio_table = self.query_one(PortfolioTable)
        chart_container = self.query_one("#chart-container")
        chart_view = self.query_one(ChartView)

        pm = PortfolioManager()
        stocks = pm.get_stocks(portfolio_table.portfolio_id)

        if stocks:
            stock_data = []
            for stock in stocks:
                stock_data.append({
                    'symbol': stock.symbol,
                    'quantity': stock.quantity,
                    'avg_price': stock.avg_price
                })

            chart_container.add_class("visible")
            chart_view.show_portfolio_chart(stock_data)
            self.notify("📊 포트폴리오 차트 표시", severity="information")
        else:
            self.notify("❌ 표시할 데이터가 없습니다", severity="error")

    def on_data_table_row_selected(self, event) -> None:
        """Handle row selection in portfolio table."""
        # Auto-update stock chart if visible
        chart_container = self.query_one("#chart-container")
        chart_view = self.query_one(ChartView)
        if chart_container.has_class("visible") and chart_view.view_mode == "stock":
            self._show_stock_chart()


def main():
    """Run the application."""
    app = MyDashApp()
    app.run()


if __name__ == "__main__":
    main()
