# PowerShell 스크립트 - 프로젝트 의존성 모듈 설치
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    프로젝트 의존성 모듈 설치 스크립트" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔍 Python 버전 확인 중..." -ForegroundColor Yellow
python --version
Write-Host ""

Write-Host "📦 가상환경 생성 및 활성화 중..." -ForegroundColor Yellow
python -m venv venv
& "venv\Scripts\Activate.ps1"
Write-Host ""

Write-Host "📥 requirements.txt에서 모듈 설치 중..." -ForegroundColor Yellow
pip install -r ../requirements.txt
Write-Host ""

Write-Host "✅ 설치 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 추천 시스템 실행:" -ForegroundColor Green
Write-Host "   python run_recommendation.py" -ForegroundColor White
Write-Host ""
Write-Host "📊 API 서버 실행:" -ForegroundColor Green
Write-Host "   python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue"
