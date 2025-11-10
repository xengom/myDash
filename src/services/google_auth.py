"""Google OAuth authentication service."""

import os
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.config.settings import settings


class GoogleAuthService:
    """Handles Google OAuth authentication."""

    # OAuth scopes for different services
    SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/tasks.readonly',
    ]

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None
    ):
        """Initialize Google auth service.

        Args:
            credentials_path: Path to credentials.json
            token_path: Path to token.json
        """
        self.credentials_path = credentials_path or settings.GOOGLE_CREDENTIALS_PATH
        self.token_path = token_path or settings.GOOGLE_TOKEN_PATH
        self._creds = None

    def get_credentials(self) -> Optional[Credentials]:
        """Get or refresh OAuth credentials.

        Returns:
            Google OAuth credentials or None if not available
        """
        # Check if credentials file exists
        if not Path(self.credentials_path).exists():
            print(f"⚠️  Google credentials not found: {self.credentials_path}")
            print("   Google 서비스를 사용하려면 credentials.json이 필요합니다")
            return None

        # Load existing token
        if Path(self.token_path).exists():
            self._creds = Credentials.from_authorized_user_file(
                self.token_path,
                self.SCOPES
            )

        # Refresh or get new credentials
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                try:
                    self._creds.refresh(Request())
                except Exception as e:
                    print(f"⚠️  Token refresh failed: {e}")
                    self._creds = None

            if not self._creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path,
                        self.SCOPES
                    )
                    self._creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"⚠️  OAuth flow failed: {e}")
                    return None

            # Save the credentials for next run
            if self._creds:
                Path(self.token_path).parent.mkdir(parents=True, exist_ok=True)
                with open(self.token_path, 'w') as token:
                    token.write(self._creds.to_json())

        return self._creds

    def is_authenticated(self) -> bool:
        """Check if user is authenticated.

        Returns:
            True if authenticated
        """
        creds = self.get_credentials()
        return creds is not None and creds.valid

    def get_calendar_service(self):
        """Get Google Calendar service.

        Returns:
            Calendar service instance or None
        """
        creds = self.get_credentials()
        if not creds:
            return None

        try:
            return build('calendar', 'v3', credentials=creds)
        except Exception as e:
            print(f"⚠️  Failed to build Calendar service: {e}")
            return None

    def get_gmail_service(self):
        """Get Gmail service.

        Returns:
            Gmail service instance or None
        """
        creds = self.get_credentials()
        if not creds:
            return None

        try:
            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            print(f"⚠️  Failed to build Gmail service: {e}")
            return None

    def get_tasks_service(self):
        """Get Google Tasks service.

        Returns:
            Tasks service instance or None
        """
        creds = self.get_credentials()
        if not creds:
            return None

        try:
            return build('tasks', 'v1', credentials=creds)
        except Exception as e:
            print(f"⚠️  Failed to build Tasks service: {e}")
            return None

    def revoke_credentials(self) -> bool:
        """Revoke OAuth credentials and delete token.

        Returns:
            True if successful
        """
        try:
            if Path(self.token_path).exists():
                os.remove(self.token_path)
            self._creds = None
            return True
        except Exception as e:
            print(f"⚠️  Failed to revoke credentials: {e}")
            return False
