"""Modal dialogs for stock operations."""

from datetime import date
from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class AddStockModal(ModalScreen[dict | None]):
    """Modal dialog for adding a new stock."""

    CSS = """
    AddStockModal {
        align: center middle;
    }

    #dialog {
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #title {
        width: 100%;
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 1;
        margin-bottom: 1;
    }

    .input-group {
        height: auto;
        margin: 1 0;
    }

    .input-group Label {
        width: 100%;
        margin-bottom: 1;
    }

    .input-group Input {
        width: 100%;
    }

    #button-row {
        width: 100%;
        height: auto;
        grid-size: 2;
        grid-gutter: 1;
        margin-top: 1;
    }

    Button {
        width: 100%;
    }

    #error-message {
        color: $error;
        width: 100%;
        text-align: center;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, portfolio_id: int):
        """Initialize add stock modal.

        Args:
            portfolio_id: Portfolio ID to add stock to
        """
        super().__init__()
        self.portfolio_id = portfolio_id

    def compose(self) -> ComposeResult:
        """Compose the modal dialog."""
        with Vertical(id="dialog"):
            yield Static("📈 주식 추가", id="title")

            with Vertical(classes="input-group"):
                yield Label("종목 심볼 (예: AAPL, GOOG)")
                yield Input(
                    placeholder="AAPL",
                    id="symbol-input"
                )

            with Vertical(classes="input-group"):
                yield Label("수량")
                yield Input(
                    placeholder="10",
                    id="quantity-input",
                    type="number"
                )

            with Vertical(classes="input-group"):
                yield Label("매수 가격 ($)")
                yield Input(
                    placeholder="150.00",
                    id="price-input",
                    type="number"
                )

            with Vertical(classes="input-group"):
                yield Label("매수 날짜 (YYYY-MM-DD, 비워두면 오늘)")
                yield Input(
                    placeholder=date.today().isoformat(),
                    id="date-input"
                )

            yield Static("", id="error-message")

            with Grid(id="button-row"):
                yield Button("추가", variant="primary", id="submit-button")
                yield Button("취소", variant="default", id="cancel-button")

    def on_mount(self) -> None:
        """Focus the symbol input when mounted."""
        self.query_one("#symbol-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button pressed event
        """
        if event.button.id == "cancel-button":
            self.dismiss(None)
        elif event.button.id == "submit-button":
            self._submit()

    def _submit(self) -> None:
        """Validate and submit the form."""
        # Get inputs
        symbol_input = self.query_one("#symbol-input", Input)
        quantity_input = self.query_one("#quantity-input", Input)
        price_input = self.query_one("#price-input", Input)
        date_input = self.query_one("#date-input", Input)
        error_msg = self.query_one("#error-message", Static)

        # Validate symbol
        symbol = symbol_input.value.strip().upper()
        if not symbol:
            error_msg.update("❌ 종목 심볼을 입력하세요")
            symbol_input.focus()
            return

        # Validate quantity
        try:
            quantity = float(quantity_input.value)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except (ValueError, TypeError):
            error_msg.update("❌ 올바른 수량을 입력하세요 (양수)")
            quantity_input.focus()
            return

        # Validate price
        try:
            price = float(price_input.value)
            if price <= 0:
                raise ValueError("Price must be positive")
        except (ValueError, TypeError):
            error_msg.update("❌ 올바른 가격을 입력하세요 (양수)")
            price_input.focus()
            return

        # Validate date
        purchase_date = None
        date_str = date_input.value.strip()
        if date_str:
            try:
                purchase_date = date.fromisoformat(date_str)
            except ValueError:
                error_msg.update("❌ 올바른 날짜 형식을 입력하세요 (YYYY-MM-DD)")
                date_input.focus()
                return

        # Return validated data
        self.dismiss({
            "portfolio_id": self.portfolio_id,
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "purchase_date": purchase_date
        })


class EditStockModal(ModalScreen[dict | None]):
    """Modal dialog for editing stock quantity/price."""

    CSS = """
    EditStockModal {
        align: center middle;
    }

    #dialog {
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #title {
        width: 100%;
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 1;
        margin-bottom: 1;
    }

    #stock-info {
        width: 100%;
        text-align: center;
        margin-bottom: 1;
        color: $text-muted;
    }

    .input-group {
        height: auto;
        margin: 1 0;
    }

    .input-group Label {
        width: 100%;
        margin-bottom: 1;
    }

    .input-group Input {
        width: 100%;
    }

    #button-row {
        width: 100%;
        height: auto;
        grid-size: 2;
        grid-gutter: 1;
        margin-top: 1;
    }

    Button {
        width: 100%;
    }

    #error-message {
        color: $error;
        width: 100%;
        text-align: center;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, stock_id: int, symbol: str, current_quantity: float, current_avg_price: float):
        """Initialize edit stock modal.

        Args:
            stock_id: Stock ID to edit
            symbol: Stock symbol
            current_quantity: Current quantity
            current_avg_price: Current average price
        """
        super().__init__()
        self.stock_id = stock_id
        self.symbol = symbol
        self.current_quantity = current_quantity
        self.current_avg_price = current_avg_price

    def compose(self) -> ComposeResult:
        """Compose the modal dialog."""
        with Vertical(id="dialog"):
            yield Static("✏️ 주식 수정", id="title")
            yield Static(f"종목: {self.symbol}", id="stock-info")

            with Vertical(classes="input-group"):
                yield Label("수량")
                yield Input(
                    value=str(self.current_quantity),
                    id="quantity-input",
                    type="number"
                )

            with Vertical(classes="input-group"):
                yield Label("평균 매수가 ($)")
                yield Input(
                    value=f"{self.current_avg_price:.2f}",
                    id="price-input",
                    type="number"
                )

            yield Static("", id="error-message")

            with Grid(id="button-row"):
                yield Button("저장", variant="primary", id="submit-button")
                yield Button("취소", variant="default", id="cancel-button")

    def on_mount(self) -> None:
        """Focus the quantity input when mounted."""
        self.query_one("#quantity-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button pressed event
        """
        if event.button.id == "cancel-button":
            self.dismiss(None)
        elif event.button.id == "submit-button":
            self._submit()

    def _submit(self) -> None:
        """Validate and submit the form."""
        quantity_input = self.query_one("#quantity-input", Input)
        price_input = self.query_one("#price-input", Input)
        error_msg = self.query_one("#error-message", Static)

        # Validate quantity
        try:
            quantity = float(quantity_input.value)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except (ValueError, TypeError):
            error_msg.update("❌ 올바른 수량을 입력하세요 (양수)")
            quantity_input.focus()
            return

        # Validate price
        try:
            price = float(price_input.value)
            if price <= 0:
                raise ValueError("Price must be positive")
        except (ValueError, TypeError):
            error_msg.update("❌ 올바른 가격을 입력하세요 (양수)")
            price_input.focus()
            return

        # Return validated data
        self.dismiss({
            "stock_id": self.stock_id,
            "quantity": quantity,
            "avg_price": price
        })


class DeleteConfirmModal(ModalScreen[bool]):
    """Modal dialog for delete confirmation."""

    CSS = """
    DeleteConfirmModal {
        align: center middle;
    }

    #dialog {
        width: 50;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #title {
        width: 100%;
        text-align: center;
        text-style: bold;
        background: $error;
        color: $text;
        padding: 1;
        margin-bottom: 1;
    }

    #message {
        width: 100%;
        text-align: center;
        margin: 2 0;
    }

    #button-row {
        width: 100%;
        height: auto;
        grid-size: 2;
        grid-gutter: 1;
        margin-top: 1;
    }

    Button {
        width: 100%;
    }
    """

    def __init__(self, item_name: str):
        """Initialize delete confirm modal.

        Args:
            item_name: Name of item to delete
        """
        super().__init__()
        self.item_name = item_name

    def compose(self) -> ComposeResult:
        """Compose the modal dialog."""
        with Vertical(id="dialog"):
            yield Static("⚠️ 삭제 확인", id="title")
            yield Static(
                f"정말로 '{self.item_name}'을(를)\n삭제하시겠습니까?",
                id="message"
            )

            with Grid(id="button-row"):
                yield Button("삭제", variant="error", id="confirm-button")
                yield Button("취소", variant="default", id="cancel-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button pressed event
        """
        self.dismiss(event.button.id == "confirm-button")
