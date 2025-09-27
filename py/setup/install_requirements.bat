@echo off
echo ========================================
echo    프로젝트 의존성 모듈 설치 스크립트
echo ========================================
echo.

echo 🔍 Python 버전 확인 중...
python --version
echo.

echo 📦 가상환경 생성 및 활성화 중...
python -m venv venv
call venv\Scripts\activate.bat
echo.

echo 📥 requirements.txt에서 모듈 설치 중...
pip install -r ../requirements.txt
echo.

echo ✅ 설치 완료!
echo.
echo 🚀 추천 시스템 실행:
echo    python run_recommendation.py
echo.
echo 📊 API 서버 실행:
echo    python -m uvicorn app.main:app --reload
echo.

pause
