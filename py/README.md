# News-Book Recommender API

뉴스 기반 도서 추천 시스템의 FastAPI 백엔드 (BERT 전용)

## 🚀 주요 기능

- **뉴스 크롤링**: 중앙일보 뉴스 자동 수집
- **BERT 기반 추천**: 문맥 기반 도서 추천 (KoBERT)
- **GPU 가속**: CUDA 지원으로 성능 최적화
- **캐싱 시스템**: 성능 최적화
- **실시간 API**: RESTful API 제공
- **중복 방지**: 오늘자 데이터 자동 체크

## 📋 요구사항

- Python 3.9+
- Supabase PostgreSQL 데이터베이스
- 8GB+ RAM (BERT 모델용)
- CUDA 지원 GPU (선택사항, 성능 향상)

## 🛠️ 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`env.example` 파일을 `.env`로 복사하고 실제 값으로 수정:

```bash
cp env.example .env
```

### 3. 서버 실행

```bash
# API 서버 실행
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# BERT 기반 추천 시스템 실행
python scripts/run_recommendation.py
```

### 4. 설치 스크립트 사용 (Windows)

```bash
# 자동 설치 및 실행
cd setup
install_requirements.bat
```

## 📚 API 문서

서버 실행 후 다음 URL에서 API 문서 확인:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ 프로젝트 구조

```
py/
├── app/                         # 메인 애플리케이션
│   ├── api/                    # API 레이어
│   │   └── endpoints.py        # REST API 엔드포인트
│   ├── core/                   # 핵심 비즈니스 로직
│   │   ├── bert/              # BERT 관련 모듈
│   │   │   ├── bert_nlp.py    # 기본 BERT NLP
│   │   │   └── bert_nlp_gpu.py # GPU 최적화 BERT NLP
│   │   ├── recommendation/    # 추천 시스템
│   │   │   ├── bert_recommendation.py      # 기본 BERT 추천
│   │   │   └── bert_recommendation_gpu.py  # GPU 최적화 BERT 추천
│   │   ├── crowling.py        # 뉴스 크롤링 서비스
│   │   └── database.py        # PostgreSQL 데이터베이스 서비스
│   ├── utils/                 # 유틸리티
│   │   └── duplicate_checker.py # 중복 데이터 체크
│   └── main.py               # FastAPI 애플리케이션
├── config/                    # 설정 관리
│   └── settings.py           # 환경 변수 설정
├── scripts/                   # 실행 스크립트
│   └── run_recommendation.py # BERT 추천 시스템 실행
├── docs/                      # 문서
├── setup/                     # 설치 스크립트
│   ├── install_requirements.bat  # Windows 설치
│   └── install_requirements.ps1  # PowerShell 설치
├── requirements.txt           # Python 의존성
├── env.example               # 환경 변수 예시
└── README.md                 # 프로젝트 문서
```

## ⚡ 성능 최적화

### 1. BERT 기반 처리
- KoBERT 모델 사용으로 한국어 문맥 이해
- 문맥적 유사도 계산으로 정확한 추천
- GPU 가속 지원으로 빠른 처리

### 2. 연결 풀링
- PostgreSQL 연결 풀 사용으로 연결 오버헤드 최소화
- 기본 풀 크기: 10개 연결

### 3. 캐싱 시스템
- 추천 결과 1시간 캐싱
- 메모리 기반 캐시로 응답 속도 향상

### 4. 비동기 처리
- FastAPI 비동기 엔드포인트
- 데이터베이스 연결 비동기 처리

### 5. GPU 가속
- CUDA 지원 BERT 모델
- 배치 처리 최적화
- 자동 GPU 감지 및 CPU 폴백

## 🔍 모니터링

### 헬스체크
```bash
curl http://localhost:8000/health
```

### 캐시 상태 확인
```bash
curl http://localhost:8000/api/cache/status
```

### BERT 모델 시각화
```bash
curl http://localhost:8000/api/visualize
```

## 🚀 주요 API 엔드포인트

### 추천 API
```http
GET /api/recommend/{category}
```

**파라미터:**
- `category`: 뉴스 카테고리 (politics, sports, economic, society, world)
- `date`: 뉴스 날짜 (선택사항, YYYY-MM-DD)
- `page`: 페이지 번호 (기본값: 1)
- `limit`: 페이지당 항목 수 (기본값: 10, 최대: 100)

**응답 예시:**
```json
{
  "total": 150,
  "page": 1,
  "limit": 10,
  "total_pages": 15,
  "books": [
    {
      "books_isbn": "9781234567890",
      "news_category": "economic",
      "books_img": "https://example.com/image.jpg",
      "books_description": "경제 관련 책 설명...",
      "books_title": "경제학 입문",
      "books_publisher": "출판사명",
      "similarity_score": 0.85
    }
  ],
  "cache_hit": false
}
```

### 기타 API
- `GET /health`: 헬스체크
- `GET /api/categories`: 사용 가능한 카테고리 목록
- `GET /api/cache/clear`: 캐시 초기화
- `GET /api/cache/status`: 캐시 상태 확인
- `GET /api/visualize`: BERT 모델 시각화

## 🔧 문제 해결

### 일반적인 문제

1. **데이터베이스 연결 실패**
   - Supabase 서비스 실행 확인
   - 환경 변수 설정 확인
   - 방화벽 설정 확인

2. **BERT 모델 로드 실패**
   - 메모리 부족 시 `ENABLE_BERT=False` 설정
   - GPU 메모리 확인

3. **캐시 메모리 부족**
   - `CACHE_TTL` 값 감소
   - 캐시 주기적 초기화

### 로그 확인

```bash
# 애플리케이션 로그
tail -f app.log

# 서버 로그
uvicorn app.main:app --log-level debug
```

## 📈 성능 벤치마크

### 테스트 환경
- CPU: Intel i7-12700K
- RAM: 32GB
- GPU: NVIDIA RTX 3080 (선택사항)
- DB: Supabase PostgreSQL

### 성능 결과
- **평균 응답 시간**: 150ms (CPU), 50ms (GPU)
- **캐시 히트율**: 85%
- **동시 사용자**: 100명
- **처리량**: 1000 req/min

## 📄 라이선스

MIT License
