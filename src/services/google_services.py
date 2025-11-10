"""Google services (Calendar, Gmail, Tasks)."""

from datetime import datetime, timedelta
from typing import Optional

from src.services.google_auth import GoogleAuthService


class GoogleCalendarService:
    """Google Calendar service."""

    def __init__(self, auth_service: Optional[GoogleAuthService] = None):
        """Initialize calendar service.

        Args:
            auth_service: Google auth service instance
        """
        self.auth = auth_service or GoogleAuthService()

    def get_upcoming_events(self, max_results: int = 10) -> list[dict]:
        """Get upcoming calendar events.

        Args:
            max_results: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        service = self.auth.get_calendar_service()
        if not service:
            return []

        try:
            # Get events from now to 7 days ahead
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Parse events
            parsed_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                parsed_events.append({
                    'summary': event.get('summary', '(No title)'),
                    'start': start,
                    'location': event.get('location', ''),
                    'description': event.get('description', ''),
                })

            return parsed_events

        except Exception as e:
            print(f"⚠️  Calendar API error: {e}")
            return []

    def format_events_summary(self, max_events: int = 5) -> str:
        """Format upcoming events for display.

        Args:
            max_events: Maximum number of events to show

        Returns:
            Formatted events string
        """
        events = self.get_upcoming_events(max_events)

        if not events:
            return "📅 일정 없음"

        lines = [f"📅 다가오는 일정 ({len(events)}개):"]
        for event in events:
            start = event['start']
            # Parse datetime
            try:
                if 'T' in start:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = dt.strftime("%m/%d %H:%M")
                else:
                    dt = datetime.fromisoformat(start)
                    time_str = dt.strftime("%m/%d")
            except:
                time_str = start

            summary = event['summary'][:30]  # Truncate long titles
            lines.append(f"  • {time_str} - {summary}")

        return "\n".join(lines)


class GmailService:
    """Gmail service."""

    def __init__(self, auth_service: Optional[GoogleAuthService] = None):
        """Initialize Gmail service.

        Args:
            auth_service: Google auth service instance
        """
        self.auth = auth_service or GoogleAuthService()

    def get_unread_count(self) -> int:
        """Get count of unread emails.

        Returns:
            Number of unread emails
        """
        service = self.auth.get_gmail_service()
        if not service:
            return 0

        try:
            result = service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=1
            ).execute()

            return result.get('resultSizeEstimate', 0)

        except Exception as e:
            print(f"⚠️  Gmail API error: {e}")
            return 0

    def get_recent_emails(self, max_results: int = 5) -> list[dict]:
        """Get recent unread emails.

        Args:
            max_results: Maximum number of emails to return

        Returns:
            List of email dictionaries
        """
        service = self.auth.get_gmail_service()
        if not service:
            return []

        try:
            # Get unread messages
            result = service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()

            messages = result.get('messages', [])
            emails = []

            for msg in messages:
                msg_data = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = {
                    h['name']: h['value']
                    for h in msg_data['payload']['headers']
                }

                emails.append({
                    'id': msg['id'],
                    'from': headers.get('From', 'Unknown'),
                    'subject': headers.get('Subject', '(No subject)'),
                    'date': headers.get('Date', ''),
                })

            return emails

        except Exception as e:
            print(f"⚠️  Gmail API error: {e}")
            return []

    def format_inbox_summary(self) -> str:
        """Format inbox summary for display.

        Returns:
            Formatted inbox string
        """
        unread_count = self.get_unread_count()

        if unread_count == 0:
            return "📧 새 메일 없음"

        emails = self.get_recent_emails(3)

        lines = [f"📧 읽지 않은 메일 {unread_count}개:"]
        for email in emails:
            subject = email['subject'][:25]  # Truncate
            sender = email['from'].split('<')[0].strip()[:20]
            lines.append(f"  • {sender}: {subject}")

        return "\n".join(lines)


class GoogleTasksService:
    """Google Tasks service."""

    def __init__(self, auth_service: Optional[GoogleAuthService] = None):
        """Initialize tasks service.

        Args:
            auth_service: Google auth service instance
        """
        self.auth = auth_service or GoogleAuthService()

    def get_tasks(self, max_results: int = 10) -> list[dict]:
        """Get tasks from default task list.

        Args:
            max_results: Maximum number of tasks to return

        Returns:
            List of task dictionaries
        """
        service = self.auth.get_tasks_service()
        if not service:
            return []

        try:
            # Get default task list
            tasklists = service.tasklists().list().execute()
            if not tasklists.get('items'):
                return []

            default_list_id = tasklists['items'][0]['id']

            # Get tasks
            results = service.tasks().list(
                tasklist=default_list_id,
                maxResults=max_results,
                showCompleted=False
            ).execute()

            tasks = results.get('items', [])

            parsed_tasks = []
            for task in tasks:
                parsed_tasks.append({
                    'title': task.get('title', '(No title)'),
                    'notes': task.get('notes', ''),
                    'due': task.get('due', ''),
                    'status': task.get('status', 'needsAction'),
                })

            return parsed_tasks

        except Exception as e:
            print(f"⚠️  Tasks API error: {e}")
            return []

    def format_tasks_summary(self, max_tasks: int = 5) -> str:
        """Format tasks for display.

        Args:
            max_tasks: Maximum number of tasks to show

        Returns:
            Formatted tasks string
        """
        tasks = self.get_tasks(max_tasks)

        if not tasks:
            return "✓ 할 일 없음"

        lines = [f"✓ 할 일 목록 ({len(tasks)}개):"]
        for task in tasks:
            title = task['title'][:30]  # Truncate
            due = task.get('due', '')

            if due:
                try:
                    dt = datetime.fromisoformat(due.replace('Z', '+00:00'))
                    due_str = f" (마감: {dt.strftime('%m/%d')})"
                except:
                    due_str = ""
            else:
                due_str = ""

            lines.append(f"  • {title}{due_str}")

        return "\n".join(lines)
