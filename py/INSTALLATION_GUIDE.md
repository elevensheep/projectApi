# 설치 가이드 (Installation Guide)

## 개요
이 프로젝트의 의존성 모듈을 설치하는 방법을 안내합니다.

## 시스템 요구사항
- Python 3.9 이상
- Windows 10/11 (PowerShell 또는 Command Prompt)
- 인터넷 연결

## 설치 방법

### 방법 1: 자동 설치 스크립트 사용 (권장)

#### Windows Command Prompt 사용
```cmd
cd py
install_requirements.bat
```

#### Windows PowerShell 사용
```powershell
cd py
.\install_requirements.ps1
```

### 방법 2: 수동 설치

#### 1. 가상환경 활성화
```cmd
cd py
venv39\Scripts\activate.bat
```

#### 2. 의존성 모듈 설치
```cmd
pip install -r requirements.txt
```

## 설치되는 모듈 목록

### 웹 프레임워크
- `fastapi==0.104.1` - FastAPI 웹 프레임워크
- `uvicorn==0.24.0` - ASGI 서버

### 데이터베이스
- `mysql-connector-python==8.2.0` - MySQL 데이터베이스 연결

### 한국어 자연어 처리
- `konlpy==0.6.0` - 한국어 형태소 분석기
- `jamo==0.4.1` - 한글 자모 분리/조합

### 머신러닝 및 클러스터링
- `gensim==4.3.2` - Word2Vec, FastText 등
- `scikit-learn==1.3.2` - 머신러닝 라이브러리
- `numpy==1.25.2` - 수치 계산 라이브러리

### 데이터 처리
- `pandas==2.1.4` - 데이터 분석 라이브러리

### 시각화
- `matplotlib==3.8.2` - 그래프 시각화
- `seaborn==0.13.0` - 통계 시각화

### 웹 스크래핑
- `requests==2.31.0` - HTTP 요청 라이브러리
- `beautifulsoup4==4.12.2` - HTML 파싱

### 기타 유틸리티
- `python-multipart==0.0.6` - 파일 업로드 지원
- `python-dotenv==1.0.0` - 환경변수 관리

## 설치 확인

### 1. 엘보우 기법 테스트
```cmd
python test_elbow_method.py
```

### 2. API 서버 실행
```cmd
python -m uvicorn app.main:app --reload
```

### 3. 브라우저에서 API 문서 확인
```
http://localhost:8000/docs
```

## 문제 해결

### 1. jamo 모듈 설치 오류
```cmd
pip install jamo==0.4.1
```

### 2. konlpy 설치 오류
```cmd
pip install konlpy==0.6.0
```

### 3. 가상환경 활성화 오류
```cmd
# PowerShell 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 또는 Command Prompt 사용
venv39\Scripts\activate.bat
```

### 4. 모듈 import 오류
```cmd
# 가상환경이 활성화되어 있는지 확인
where python

# pip 업그레이드
python -m pip install --upgrade pip
```

## 추가 설정

### 1. 환경변수 설정 (.env 파일)
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database
```

### 2. MySQL 데이터베이스 설정
- MySQL 서버가 실행 중인지 확인
- 데이터베이스 연결 정보 확인
- 필요한 테이블이 생성되어 있는지 확인

## 개발 환경 설정

### 1. IDE 설정 (VS Code)
- Python 확장 설치
- 가상환경 인터프리터 선택
- `.vscode/settings.json` 설정

### 2. Git 설정
```cmd
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 성능 최적화

### 1. 메모리 사용량 최적화
- 단어 수 제한 (word_count 파라미터)
- 클러스터 수 제한 (max_clusters 파라미터)

### 2. 실행 시간 최적화
- t-SNE iterations 조정
- PCA components 수 조정

## 지원

문제가 발생하면 다음을 확인하세요:
1. Python 버전 (3.9 이상)
2. 가상환경 활성화 상태
3. 인터넷 연결 상태
4. 방화벽 설정

추가 도움이 필요하면 프로젝트 이슈를 생성해주세요.
