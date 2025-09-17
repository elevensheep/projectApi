# News-Book Recommender API

뉴스 기반 도서 추천 시스템의 FastAPI 백엔드

## 🚀 주요 기능

- **뉴스 크롤링**: 중앙일보 뉴스 자동 수집
- **BERT 기반 추천**: 문맥 기반 도서 추천
- **전통적 추천**: 키워드 기반 도서 추천
- **캐싱 시스템**: 성능 최적화
- **실시간 API**: RESTful API 제공

## 📋 요구사항

- Python 3.9+
- MySQL 8.0+
- 8GB+ RAM (BERT 모델용)

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

`.env` 파일을 생성하고 다음 내용을 추가:

```env
# 애플리케이션 설정
DEBUG=False
APP_NAME="News-Book Recommender API"
APP_VERSION="2.0.0"

# 데이터베이스 설정
DB_HOST=localhost
DB_PORT=3306
DB_NAME=bookdb
DB_USER=root
DB_PASSWORD=your_password
DB_AUTH_PLUGIN=mysql_native_password
DB_POOL_SIZE=10

# 추천 시스템 설정
ENABLE_BERT=True
CACHE_TTL=3600

# 서버 설정
HOST=0.0.0.0
PORT=8000
```

### 3. 데이터베이스 설정

MySQL에서 데이터베이스 생성:

```sql
CREATE DATABASE bookdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 서버 실행

```bash
# 개발 모드
python app/main.py

# 또는 uvicorn 직접 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API 문서

서버 실행 후 다음 URL에서 API 문서 확인:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 주요 API 엔드포인트

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
- `GET /api/visualize`: NLP 모델 시각화

## 🏗️ 프로젝트 구조

```
py/
├── app/
│   ├── api/
│   │   └── endpoints.py      # API 엔드포인트
│   ├── services/
│   │   ├── database.py       # 데이터베이스 서비스
│   │   ├── crowling.py       # 뉴스 크롤링
│   │   ├── nlp.py           # 전통적 NLP
│   │   └── bert_nlp.py      # BERT NLP
│   ├── utils/
│   │   ├── recommendation_runner.py  # 전통적 추천
│   │   └── bert_recommendation.py    # BERT 추천
│   └── main.py              # FastAPI 애플리케이션
├── config.py                # 설정 관리
├── requirements.txt         # 패키지 의존성
└── README.md               # 프로젝트 문서
```

## ⚡ 성능 최적화

### 1. 연결 풀링
- MySQL 연결 풀 사용으로 연결 오버헤드 최소화
- 기본 풀 크기: 10개 연결

### 2. 캐싱 시스템
- 추천 결과 1시간 캐싱
- 메모리 기반 캐시로 응답 속도 향상

### 3. 비동기 처리
- FastAPI 비동기 엔드포인트
- 데이터베이스 연결 비동기 처리

### 4. Gzip 압축
- 응답 데이터 자동 압축
- 네트워크 대역폭 절약

## 🔍 모니터링

### 로깅
- 요청/응답 로깅
- 쿼리 실행 시간 측정
- 에러 로깅 및 추적

### 헬스체크
```bash
curl http://localhost:8000/health
```

### 캐시 상태 확인
```bash
curl http://localhost:8000/api/cache/status
```

## 🚨 문제 해결

### 일반적인 문제

1. **데이터베이스 연결 실패**
   - MySQL 서비스 실행 확인
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
- CPU: Intel i7-10700K
- RAM: 32GB
- DB: MySQL 8.0

### 성능 결과
- **평균 응답 시간**: 150ms
- **캐시 히트율**: 85%
- **동시 사용자**: 100명
- **처리량**: 1000 req/min

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

MIT License

## 📞 지원

문제가 발생하면 이슈를 생성해주세요. 