#!/usr/bin/env python3
"""Setup Google OAuth authentication."""

import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/tasks.readonly',
]

CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', '.credential.json')
TOKEN_PATH = os.getenv('GOOGLE_TOKEN_PATH', '.token.json')


def setup_google_auth():
    """Run Google OAuth flow."""
    print("🔐 Google OAuth 인증 설정")
    print("=" * 60)

    # Check credentials file
    if not Path(CREDENTIALS_PATH).exists():
        print(f"\n❌ Credentials 파일을 찾을 수 없습니다: {CREDENTIALS_PATH}")
        print("\n설정 방법:")
        print("1. https://console.cloud.google.com/ 접속")
        print("2. 프로젝트 생성 또는 선택")
        print("3. API 및 서비스 > 라이브러리")
        print("   - Google Calendar API 활성화")
        print("   - Gmail API 활성화")
        print("   - Google Tasks API 활성화")
        print("4. API 및 서비스 > 사용자 인증 정보")
        print("5. OAuth 2.0 클라이언트 ID 생성 (데스크톱 앱)")
        print("6. credentials.json 다운로드")
        print(f"7. 파일을 '{CREDENTIALS_PATH}'로 저장")
        return False

    print(f"✓ Credentials 파일 발견: {CREDENTIALS_PATH}")

    creds = None

    # Check if token already exists
    if Path(TOKEN_PATH).exists():
        print(f"✓ Token 파일 발견: {TOKEN_PATH}")
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            print("✓ 기존 토큰 로드 성공")
        except Exception as e:
            print(f"⚠️  기존 토큰 로드 실패: {e}")
            creds = None

    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 토큰 갱신 중...")
            try:
                creds.refresh(Request())
                print("✓ 토큰 갱신 성공")
            except Exception as e:
                print(f"❌ 토큰 갱신 실패: {e}")
                creds = None

        if not creds:
            print("\n🌐 OAuth 인증 시작...")
            print("   브라우저가 열리면 Google 계정으로 로그인하세요.")
            print("   앱에 다음 권한을 허용해주세요:")
            print("   - Google Calendar (읽기 전용)")
            print("   - Gmail (읽기 전용)")
            print("   - Google Tasks (읽기 전용)")

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES
                )
                # Try to run local server first
                try:
                    creds = flow.run_local_server(port=0)
                    print("\n✅ 인증 성공!")
                except Exception as e:
                    print(f"\n⚠️  로컬 서버 실행 실패: {e}")
                    print("\n대안: 수동 인증 방법")
                    print("1. 다음 URL을 브라우저에서 열어주세요:")

                    # Manual auth flow
                    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    print(f"\n{auth_url}\n")
                    print("2. 인증 후 표시되는 코드를 복사하세요")
                    auth_code = input("3. 코드를 여기에 붙여넣으세요: ").strip()

                    flow.fetch_token(code=auth_code)
                    creds = flow.credentials
                    print("\n✅ 수동 인증 성공!")

            except Exception as e:
                print(f"\n❌ OAuth 인증 실패: {e}")
                return False

        # Save credentials
        print(f"\n💾 토큰 저장 중: {TOKEN_PATH}")
        try:
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
            print("✓ 토큰 저장 성공")
        except Exception as e:
            print(f"❌ 토큰 저장 실패: {e}")
            return False
    else:
        print("✓ 유효한 토큰이 이미 존재합니다")

    # Test the credentials
    print("\n🧪 인증 테스트 중...")
    try:
        from googleapiclient.discovery import build

        # Test Calendar API
        print("  - Calendar API 테스트...", end=" ")
        calendar_service = build('calendar', 'v3', credentials=creds)
        events_result = calendar_service.events().list(
            calendarId='primary',
            maxResults=1,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        print("✓")

        # Test Gmail API
        print("  - Gmail API 테스트...", end=" ")
        gmail_service = build('gmail', 'v1', credentials=creds)
        results = gmail_service.users().messages().list(
            userId='me', maxResults=1
        ).execute()
        print("✓")

        # Test Tasks API
        print("  - Tasks API 테스트...", end=" ")
        tasks_service = build('tasks', 'v1', credentials=creds)
        results = tasks_service.tasklists().list(maxResults=1).execute()
        print("✓")

        print("\n✅ 모든 API 테스트 통과!")
        print("\n🎉 Google 서비스 설정 완료!")
        print(f"\n이제 myDash를 실행하세요: ./run.sh")
        return True

    except Exception as e:
        print(f"\n❌ API 테스트 실패: {e}")
        print("\n문제 해결:")
        print("1. Google Cloud Console에서 API가 활성화되어 있는지 확인")
        print("2. OAuth 동의 화면이 올바르게 설정되어 있는지 확인")
        print("3. 앱이 '테스트' 상태인 경우 테스트 사용자로 추가되어 있는지 확인")
        return False


if __name__ == '__main__':
    import sys
    success = setup_google_auth()
    sys.exit(0 if success else 1)
