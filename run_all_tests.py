"""Run all test suites."""

import sys
import subprocess
from pathlib import Path


def run_test(test_file: str, description: str) -> bool:
    """Run a test file and report results.

    Args:
        test_file: Path to test file
        description: Test description

    Returns:
        True if test passed
    """
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print('='*60)

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            timeout=60
        )
        success = result.returncode == 0
        if success:
            print(f"✅ {description} 통과")
        else:
            print(f"❌ {description} 실패 (exit code: {result.returncode})")
        return success
    except subprocess.TimeoutExpired:
        print(f"⏱️  {description} 타임아웃 (60초)")
        return False
    except Exception as e:
        print(f"❌ {description} 오류: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 myDash 전체 테스트 스위트")
    print("="*60)

    tests = [
        ("test_system_monitoring.py", "시스템 모니터링 테스트"),
        ("test_stock_service.py", "주식 서비스 테스트"),
        ("test_end_to_end.py", "포트폴리오 End-to-End 테스트"),
        ("test_google_services.py", "Google 서비스 테스트"),
    ]

    results = []
    for test_file, description in tests:
        test_path = Path(test_file)
        if not test_path.exists():
            print(f"⚠️  테스트 파일 없음: {test_file}")
            results.append((description, False))
            continue

        success = run_test(test_file, description)
        results.append((description, success))

    # Summary
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for description, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{status}: {description}")

    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
        return 0
    else:
        print(f"\n⚠️  {total - passed}개 테스트가 실패했습니다.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
