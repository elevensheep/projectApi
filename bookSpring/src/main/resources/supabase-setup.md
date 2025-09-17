# Supabase 데이터베이스 설정 가이드

## 1. Supabase 프로젝트 생성

1. [Supabase](https://supabase.com)에 로그인
2. "New Project" 클릭
3. 프로젝트 이름과 데이터베이스 비밀번호 설정
4. 지역 선택 (한국: Northeast Asia - Seoul)

## 2. 데이터베이스 연결 정보 확인

1. 프로젝트 대시보드에서 "Settings" > "Database" 이동
2. "Connection string" 섹션에서 정보 확인:
   - **Host**: `db.your-project-ref.supabase.co`
   - **Port**: `6543` (Transaction pooler)
   - **Database**: `postgres`
   - **Username**: `postgres`
   - **Password**: 설정한 비밀번호

## 3. 환경 변수 설정

### 방법 1: application.properties 직접 수정
```properties
spring.datasource.url=jdbc:postgresql://db.your-project-ref.supabase.co:6543/postgres?sslmode=require
spring.datasource.username=postgres
spring.datasource.password=your-actual-password
```

### 방법 2: 환경 변수 사용 (권장)
```bash
# Windows (PowerShell)
$env:SUPABASE_DB_URL="jdbc:postgresql://db.your-project-ref.supabase.co:6543/postgres?sslmode=require"
$env:SUPABASE_DB_USER="postgres"
$env:SUPABASE_DB_PASSWORD="your-actual-password"

# Linux/Mac
export SUPABASE_DB_URL="jdbc:postgresql://db.your-project-ref.supabase.co:6543/postgres?sslmode=require"
export SUPABASE_DB_USER="postgres"
export SUPABASE_DB_PASSWORD="your-actual-password"
```

## 4. 데이터베이스 스키마 생성

Supabase SQL Editor에서 다음 스크립트 실행:

```sql
-- 사용자 테이블
CREATE TABLE tb_user (
    user_id BIGSERIAL PRIMARY KEY,
    user_uuid VARCHAR(255) UNIQUE NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    user_nickname VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 도서 테이블
CREATE TABLE tb_book (
    book_id BIGSERIAL PRIMARY KEY,
    book_title VARCHAR(500) NOT NULL,
    book_author VARCHAR(200),
    book_publisher VARCHAR(200),
    book_isbn VARCHAR(20) UNIQUE,
    book_description TEXT,
    book_image_url VARCHAR(1000),
    book_category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 북마크 테이블
CREATE TABLE tb_bookmark (
    bookmark_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES tb_user(user_id),
    book_id BIGINT REFERENCES tb_book(book_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, book_id)
);

-- 추천 테이블
CREATE TABLE tb_recommend (
    recommend_id BIGSERIAL PRIMARY KEY,
    book_id BIGINT REFERENCES tb_book(book_id),
    category VARCHAR(50) NOT NULL,
    similarity_score DECIMAL(5,4),
    method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 뉴스 키워드 테이블
CREATE TABLE tb_news_keyword (
    keyword_id BIGSERIAL PRIMARY KEY,
    keyword VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    news_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 도서 키워드 테이블
CREATE TABLE tb_book_keyword (
    book_keyword_id BIGSERIAL PRIMARY KEY,
    book_id BIGINT REFERENCES tb_book(book_id),
    keyword VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_tb_user_uuid ON tb_user(user_uuid);
CREATE INDEX idx_tb_book_category ON tb_book(book_category);
CREATE INDEX idx_tb_bookmark_user_id ON tb_bookmark(user_id);
CREATE INDEX idx_tb_recommend_category ON tb_recommend(category);
CREATE INDEX idx_tb_news_keyword_category_date ON tb_news_keyword(category, news_date);
CREATE INDEX idx_tb_book_keyword_book_id ON tb_book_keyword(book_id);
```

## 5. 연결 테스트

애플리케이션 실행 후 로그에서 다음 메시지 확인:
```
✅ PostgreSQL 연결 성공!
✅ PostgreSQL 연결 풀 초기화 성공!
```

## 6. 문제 해결

### 연결 실패 시
1. 방화벽 설정 확인
2. Supabase 프로젝트 상태 확인
3. 연결 정보 정확성 확인
4. SSL 모드 확인 (`sslmode=require`)

### 성능 최적화
1. Connection Pool 크기 조정
2. 적절한 인덱스 설정
3. 쿼리 최적화
4. Supabase 대시보드에서 성능 모니터링
