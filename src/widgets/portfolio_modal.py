"""Modal dialogs for portfolio operations."""

from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class AddPortfolioModal(ModalScreen[str | None]):
    """Modal dialog for creating a new portfolio."""

    CSS = """
    AddPortfolioModal {
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

    def compose(self) -> ComposeResult:
        """Compose the modal dialog."""
        with Vertical(id="dialog"):
            yield Static("📁 새 포트폴리오", id="title")

            with Vertical(classes="input-group"):
                yield Label("포트폴리오 이름")
                yield Input(
                    placeholder="예: 내 포트폴리오",
                    id="name-input"
                )

            yield Static("", id="error-message")

            with Grid(id="button-row"):
                yield Button("생성", variant="primary", id="submit-button")
                yield Button("취소", variant="default", id="cancel-button")

    def on_mount(self) -> None:
        """Focus the name input when mounted."""
        self.query_one("#name-input", Input).focus()

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
        name_input = self.query_one("#name-input", Input)
        error_msg = self.query_one("#error-message", Static)

        name = name_input.value.strip()
        if not name:
            error_msg.update("❌ 포트폴리오 이름을 입력하세요")
            name_input.focus()
            return

        self.dismiss(name)


class EditPortfolioModal(ModalScreen[str | None]):
    """Modal dialog for editing portfolio name."""

    CSS = """
    EditPortfolioModal {
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

    def __init__(self, current_name: str):
        """Initialize edit portfolio modal.

        Args:
            current_name: Current portfolio name
        """
        super().__init__()
        self.current_name = current_name

    def compose(self) -> ComposeResult:
        """Compose the modal dialog."""
        with Vertical(id="dialog"):
            yield Static("✏️ 포트폴리오 이름 변경", id="title")

            with Vertical(classes="input-group"):
                yield Label("포트폴리오 이름")
                yield Input(
                    value=self.current_name,
                    id="name-input"
                )

            yield Static("", id="error-message")

            with Grid(id="button-row"):
                yield Button("저장", variant="primary", id="submit-button")
                yield Button("취소", variant="default", id="cancel-button")

    def on_mount(self) -> None:
        """Focus and select the name input when mounted."""
        name_input = self.query_one("#name-input", Input)
        name_input.focus()
        # Select all text for easy replacement
        name_input.action_end()
        name_input.action_select_all()

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
        name_input = self.query_one("#name-input", Input)
        error_msg = self.query_one("#error-message", Static)

        name = name_input.value.strip()
        if not name:
            error_msg.update("❌ 포트폴리오 이름을 입력하세요")
            name_input.focus()
            return

        self.dismiss(name)

