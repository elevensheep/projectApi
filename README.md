# 프로젝트 전체 실행 스크립트

이 프로젝트는 스프링 부트, 리액트, FastAPI로 구성된 풀스택 애플리케이션입니다.

## 📋 사전 요구사항

다음 프로그램들이 시스템에 설치되어 있어야 합니다:

- **Java 17 이상** - Spring Boot 실행용
- **Node.js** - React 개발 서버 실행용
- **Python 3.8 이상** - FastAPI 실행용

## 🚀 빠른 시작

### Windows 환경

#### 방법 1: 배치 파일 사용 (권장)
```bash
# 모든 서비스 시작
start-all.bat

# 모든 서비스 종료
stop-all.bat
```

#### 방법 2: PowerShell 스크립트 사용
```powershell
# PowerShell에서 실행
.\start-all.ps1
```

### 수동 실행

각 서비스를 개별적으로 실행하려면:

#### 1. FastAPI 서버 (포트: 8000)
```bash
cd py
python -m venv venv39
venv39\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Spring Boot 서버 (포트: 8080)
```bash
cd bookSpring
./gradlew bootRun
```

#### 3. React 개발 서버 (포트: 3000)
```bash
cd frontend
npm install
npm start
```

## 🌐 서비스 접속 주소

스크립트 실행 후 다음 주소로 접속할 수 있습니다:

- **React Frontend**: http://localhost:3000
- **Spring Boot API**: http://localhost:8080
- **FastAPI**: http://localhost:8000
- **FastAPI 문서**: http://localhost:8000/docs
- **Spring Boot Swagger**: http://localhost:8080/swagger-ui/index.html

## 📁 프로젝트 구조

```
projectApi/
├── bookSpring/          # Spring Boot 백엔드
│   ├── src/main/java/com/book/book/
│   │   ├── controller/  # REST API 컨트롤러
│   │   ├── service/     # 비즈니스 로직
│   │   ├── repository/  # 데이터 접근 계층
│   │   ├── entity/      # JPA 엔티티
│   │   ├── dto/         # 데이터 전송 객체
│   │   ├── config/      # 설정 클래스
│   │   ├── jwt/         # JWT 관련
│   │   └── exception/   # 예외 처리
│   └── src/main/resources/
│       └── application.properties
├── frontend/           # React 프론트엔드
├── py/                 # FastAPI 서비스
├── start-all.bat       # Windows 배치 실행 스크립트
├── stop-all.bat        # Windows 배치 종료 스크립트
├── start-all.ps1       # PowerShell 실행 스크립트
└── README.md           # 이 파일
```

## 🔧 스프링 부트 최적화 내용

### 1. 코드 구조 개선
- **중복 의존성 제거**: TbUserController에서 중복된 TbUserRepository 제거
- **일관된 응답 형식**: ApiResponse<T> 클래스로 통일된 응답 구조 적용
- **예외 처리 강화**: GlobalExceptionHandler로 전역 예외 처리 구현

### 2. 보안 설정 개선
- **JWT 인증**: 안전한 토큰 기반 인증 구현
- **CORS 설정**: 프론트엔드와의 안전한 통신
- **권한 관리**: 엔드포인트별 접근 권한 세분화

### 3. 로깅 시스템
- **구조화된 로깅**: SLF4J + Logback 사용
- **레벨별 로깅**: DEBUG, INFO, WARN, ERROR 레벨 구분
- **성능 모니터링**: SQL 쿼리 로깅 및 성능 추적

### 4. API 문서화
- **Swagger UI**: 자동 API 문서 생성
- **상세한 API 설명**: 각 엔드포인트별 설명 및 예시

### 5. 성능 최적화
- **페이징 처리**: 대용량 데이터 처리 최적화
- **비동기 처리**: Reactor를 사용한 비동기 API 호출
- **캐싱**: 적절한 캐싱 전략 적용

## ⚠️ 주의사항

1. **포트 충돌**: 3000, 8080, 8000 포트가 사용 중이지 않은지 확인하세요.
2. **의존성 설치**: 스크립트는 자동으로 필요한 의존성을 설치합니다.
3. **가상환경**: Python 가상환경이 자동으로 생성됩니다.
4. **서버 종료**: 각 터미널 창을 닫거나 `stop-all.bat`를 실행하여 서버를 종료할 수 있습니다.
5. **데이터베이스**: MySQL이 실행 중이어야 합니다.

## 🔧 문제 해결

### 포트가 이미 사용 중인 경우
```bash
# Windows에서 포트 사용 중인 프로세스 확인
netstat -ano | findstr :3000
netstat -ano | findstr :8080
netstat -ano | findstr :8000

# 프로세스 종료 (PID는 위 명령어로 확인)
taskkill /f /pid [PID]
```

### 권한 문제
PowerShell 스크립트 실행 시 권한 오류가 발생하면:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Java 버전 문제
Spring Boot는 Java 17 이상이 필요합니다:
```bash
java -version
```

### 데이터베이스 연결 문제
MySQL이 실행 중인지 확인하고, 데이터베이스가 생성되어 있는지 확인하세요:
```sql
CREATE DATABASE IF NOT EXISTS book_db;
```

## 📝 로그 확인

각 서비스의 로그는 별도의 터미널 창에서 확인할 수 있습니다:
- FastAPI: FastAPI Server 창
- Spring Boot: Spring Boot Server 창  
- React: React Development Server 창

### 로그 레벨 설정
`application.properties`에서 로그 레벨을 조정할 수 있습니다:
```properties
# 개발 환경
logging.level.com.book.book=DEBUG

# 운영 환경
logging.level.com.book.book=INFO
```

## 🚀 배포 가이드

### 개발 환경
- 모든 서비스가 로컬에서 실행됩니다.
- 핫 리로드가 활성화되어 있습니다.

### 운영 환경
- 각 서비스를 별도 서버에 배포합니다.
- 환경 변수를 통한 설정 관리가 필요합니다.
- 로그 레벨을 INFO로 설정합니다. 