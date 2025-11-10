"""Google services panel widget."""

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical

from src.services import (
    GoogleAuthService,
    GoogleCalendarService,
    GmailService,
    GoogleTasksService,
)


class GooglePanel(Vertical):
    """Panel displaying Google services information."""

    def __init__(self):
        """Initialize Google panel."""
        super().__init__()
        self.auth = GoogleAuthService()
        self.calendar = GoogleCalendarService(self.auth)
        self.gmail = GmailService(self.auth)
        self.tasks = GoogleTasksService(self.auth)
        self._authenticated = False

    def compose(self) -> ComposeResult:
        """Compose the panel layout."""
        yield Static("🌐 Google 서비스", classes="panel-title")
        yield Static("", id="google-content")

    def on_mount(self) -> None:
        """Setup when widget is mounted."""
        self._authenticated = self.auth.is_authenticated()
        self.refresh_data()
        # Refresh every 5 minutes
        self.set_interval(300.0, self.refresh_data)

    def refresh_data(self) -> None:
        """Refresh Google services data."""
        content_widget = self.query_one("#google-content", Static)

        if not self._authenticated:
            content_widget.update(
                "\n[dim]Google 서비스가 설정되지 않았습니다[/dim]\n\n"
                "사용 방법:\n"
                "1. Google Cloud Console에서\n"
                "   credentials.json 다운로드\n"
                "2. 프로젝트 루트에 저장\n"
                "3. 앱 재시작 후 OAuth 인증\n\n"
                "[dim]선택 사항입니다[/dim]"
            )
            return

        try:
            # Get data from all services
            calendar_summary = self.calendar.format_events_summary(3)
            gmail_summary = self.gmail.format_inbox_summary()
            tasks_summary = self.tasks.format_tasks_summary(3)

            # Combine into display
            content = f"{calendar_summary}\n\n{gmail_summary}\n\n{tasks_summary}"
            content_widget.update(content)

        except Exception as e:
            content_widget.update(
                f"[red]⚠️  오류 발생[/red]\n\n{str(e)}\n\n"
                "[dim]Google API 설정을 확인하세요[/dim]"
            )
