# myDash - Personal Dashboard TUI

터미널 기반의 개인 대시보드 애플리케이션입니다. 주식 포트폴리오 관리, 시스템 모니터링, 날씨 정보를 하나의 화면에서 확인할 수 있습니다.

![myDash](./docs/screenshot.png)

## 주요 기능

### 📈 포트폴리오 관리
- **실시간 주가**: yfinance를 통한 실시간 주식 가격 조회
- **가중 평균 계산**: 추가 매수 시 자동 평균 단가 계산
- **손익 계산**: 실시간 평가액과 손익률 표시
- **거래 내역**: 모든 매수/매도 거래 기록 추적
- **CRUD 기능**: 주식 추가/수정/삭제
- **📊 차트 시각화**:
  - 주식 선택 시: 3개월 가격 추이, 평균 단가 비교
  - 포트폴리오 전체: 자산 배분, 개별 수익률 차트

### 🖥️ 시스템 모니터링
- **사용자 정보**: whoami (user@hostname)
- **리소스 모니터링**: CPU 및 메모리 사용률 실시간 표시
- **시간 정보**: 현재 시간 표시
- **날씨 정보**: OpenWeatherMap API 연동 (선택사항)

### 🌐 Google 서비스 (선택사항)
- **Google Calendar**: 다가오는 일정 조회
- **Gmail**: 읽지 않은 메일 개수 및 최근 메일
- **Google Tasks**: 할 일 목록 표시

## 설치

### 요구사항
- Python 3.10 이상
- pip (Python 패키지 관리자)

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd myDash
```

### 2. 가상 환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 데이터베이스 초기화
```bash
python -m src.database.migrations
```

## 설정

### 환경 변수 (.env)
프로젝트 루트에 `.env` 파일을 생성하세요:

```env
# 데이터베이스
DATABASE_PATH=./data/mydash.db

# OpenWeather API (선택사항)
OPENWEATHER_API_KEY=your_api_key_here
WEATHER_CITY=Seoul

# Google OAuth (선택사항)
GOOGLE_CREDENTIALS_PATH=.credentials.json
GOOGLE_TOKEN_PATH=.token.json
```

### OpenWeather API 설정 (선택사항)
1. [OpenWeatherMap](https://openweathermap.org/api) 가입
2. API 키 발급
3. `.env`에 API 키 추가

### Google 서비스 설정 (선택사항)
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성
3. API 활성화:
   - Google Calendar API
   - Gmail API
   - Google Tasks API
4. OAuth 2.0 클라이언트 ID 생성 (데스크톱 앱)
5. `credentials.json` 다운로드 후 프로젝트 루트에 저장
6. 첫 실행 시 브라우저에서 OAuth 인증 진행

## 실행

```bash
python -m src.main
```

## 키보드 단축키

| 키 | 기능 |
|---|------|
| `a` | 주식 추가 |
| `e` | 주식 수정 |
| `d` | 주식 삭제 |
| `v` | 차트 보기/숨기기 |
| `r` | 새로고침 |
| `q` | 종료 |

### 차트 사용법

1. **주식 개별 차트 보기**:
   - 포트폴리오 테이블에서 주식 선택 (화살표 키)
   - `v` 키 누르기
   - 3개월 가격 추이, 평균 단가 비교 표시

2. **포트폴리오 전체 차트 보기**:
   - 주식 선택 없이 `v` 키 누르기
   - 자산 배분 및 개별 수익률 차트 표시

3. **차트 숨기기**: `v` 키 다시 누르기

4. **자동 업데이트**: 차트가 표시된 상태에서 다른 주식 선택 시 자동으로 해당 주식 차트로 전환

## 프로젝트 구조

```
myDash/
├── src/
│   ├── config/           # 설정 파일
│   │   └── settings.py
│   ├── database/         # 데이터베이스 관리
│   │   ├── db_manager.py
│   │   └── migrations.py
│   ├── models/           # 데이터 모델
│   │   ├── portfolio.py
│   │   ├── stock.py
│   │   └── transaction.py
│   ├── services/         # 비즈니스 로직
│   │   ├── portfolio_manager.py
│   │   ├── stock_service.py
│   │   ├── system_service.py
│   │   ├── weather_service.py
│   │   ├── chart_service.py
│   │   ├── google_auth.py
│   │   └── google_services.py
│   ├── widgets/          # UI 위젯
│   │   ├── portfolio_table.py
│   │   ├── stock_modal.py
│   │   ├── portfolio_modal.py
│   │   ├── google_panel.py
│   │   └── chart_view.py
│   └── main.py           # 메인 앱
├── tests/                # 테스트
├── data/                 # 데이터 파일
├── docs/                 # 문서
├── requirements.txt      # Python 의존성
└── README.md
```

## 기술 스택

- **UI**: [Textual](https://github.com/Textualize/textual) - Modern TUI framework
- **Database**: SQLite with row factory
- **Stock Data**: [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance API
- **System Monitoring**: [psutil](https://github.com/giampaolo/psutil) - System utilities
- **Weather**: [OpenWeatherMap API](https://openweathermap.org/api)
- **Google APIs**: google-api-python-client

## 주요 기능 상세

### 가중 평균 계산
추가 매수 시 평균 단가를 자동으로 계산합니다:

```
새 평균가 = (기존 수량 × 기존 평균가 + 추가 수량 × 추가 가격) / (기존 수량 + 추가 수량)
```

예시:
- 기존: AAPL 10주 @ $150
- 추가 매수: AAPL 5주 @ $160
- 결과: AAPL 15주 @ $153.33

### 실시간 데이터 갱신
- **주식 가격**: 5분 캐시 (yfinance API 제한 고려)
- **시스템 상태**: 1초마다 업데이트 (CPU, 메모리, 시간)
- **날씨 정보**: 10분 캐시 (API 호출 최소화)
- **Google 서비스**: 5분마다 갱신

### 데이터베이스 스키마
- **portfolios**: 포트폴리오 정보
- **stocks**: 주식 정보 (가중 평균가 포함)
- **transactions**: 거래 내역 (매수/매도)

CASCADE DELETE로 데이터 무결성 보장

## 테스트

```bash
# 시스템 모니터링 테스트
python test_system_monitoring.py

# 주식 서비스 테스트
python test_stock_service.py

# 포트폴리오 End-to-End 테스트
python test_end_to_end.py

# Google 서비스 테스트
python test_google_services.py
```

## 문제 해결

### yfinance 데이터를 가져올 수 없음
- 인터넷 연결 확인
- Yahoo Finance API 상태 확인
- 종목 심볼이 올바른지 확인 (예: AAPL, GOOG, MSFT)

### 날씨 정보가 표시되지 않음
- `.env`에 `OPENWEATHER_API_KEY` 설정 확인
- API 키가 유효한지 확인
- 도시 이름이 올바른지 확인

### Google 서비스가 작동하지 않음
- `credentials.json` 파일이 프로젝트 루트에 있는지 확인
- Google Cloud Console에서 필요한 API가 활성화되었는지 확인
- OAuth 인증 진행 (첫 실행 시 브라우저 열림)

## 개발 히스토리

- **Phase 1**: 기본 인프라 및 데이터베이스 (2025-11-10)
- **Phase 2**: 포트폴리오 관리 및 CRUD 모달 (2025-11-10)
- **Phase 3**: 시스템 모니터링 및 날씨 정보 (2025-11-10)
- **Phase 4**: Google 서비스 통합 (2025-11-10)
- **Phase 5**: 최적화 및 문서화 (2025-11-10)

## 라이선스

MIT License

## 기여

버그 리포트와 기능 제안은 환영합니다!

## 개발자

개발: Claude Code + Human collaboration
프레임워크: Textual (Python TUI)
