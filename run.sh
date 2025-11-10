#!/bin/bash
# myDash 실행 스크립트

# 가상 환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ 가상 환경이 없습니다. 먼저 설치하세요:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# 데이터 디렉토리 생성
mkdir -p data

# myDash 실행
python -m src.main
