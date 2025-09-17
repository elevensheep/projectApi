<!-- PROJECT BADGES -->
<p align="center">
  <img src="https://img.shields.io/badge/Project-BookTrend-111111?style=for-the-badge">
  <img src="https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=white&style=for-the-badge">
  <img src="https://img.shields.io/badge/SpringBoot-6DB33F?logo=springboot&logoColor=white&style=for-the-badge">
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white&style=for-the-badge">
  <img src="https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white&style=for-the-badge">
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white&style=for-the-badge">
  <img src="https://img.shields.io/badge/Konlpy-006600?style=for-the-badge">
  <img src="https://img.shields.io/badge/License-MIT-000000?style=for-the-badge">
</p>

<h1 align="center">📚 BookTrend — 뉴스 키워드 기반 도서 추천 플랫폼</h1>

<p align="center">
  <em>오늘의 뉴스로, 오늘의 책을 만나다.</em><br/>
  뉴스 제목에서 추출한 키워드로 트렌디한 도서를 추천하는 서비스입니다.
</p>

---

## 목차
- [개요](#개요)
- [핵심 기능](#핵심-기능)
- [기술 스택](#기술-스택)
- [아키텍처](#아키텍처)
- [스크린샷](#스크린샷)
- [프로젝트 구조](#프로젝트-구조)
- [빠른 시작](#빠른-시작)
- [환경 변수](#환경-변수)
- [API 개요](#api-개요)
- [데이터 파이프라인](#데이터-파이프라인)
- [트러블슈팅](#트러블슈팅)
- [로드맵](#로드맵)
- [팀](#팀)
- [라이선스](#라이선스)

---

## 개요
**BookTrend**는 뉴스 데이터(제목/키워드)를 수집·전처리하고, K-Means 클러스터링으로 이슈를 묶어 관련 도서를 추천합니다.  
- **목표**
  - 최신 이슈와 관련된 도서를 자동 추천
  - 새로운 책 탐색 유도 및 독서 활성화
  - 공공/상용 도서 API와의 연동으로 메타데이터·재고 확인

---

## 핵심 기능
- 📰 **뉴스 수집**: BeautifulSoup + requests로 다수 언론사 크롤링
- 🔤 **한국어 전처리**: Konlpy 형태소 분석, 불용어 제거, 정규화
- 📊 **추천 알고리즘**: scikit-learn K-Means + 실루엣 점수로 k 최적화
- 📚 **도서 연동**: 국립중앙도서관 OpenAPI(메타데이터), 알라딘 OpenAPI(판매/재고)
- 💻 **웹 UI**: React 기반 검색/추천/상세 화면
- 🧩 **백엔드**: Spring Boot (서비스/도메인), FastAPI(크롤링·NLP 마이크로서비스)
- 🧾 **문서화**: Swagger(OpenAPI) 자동 문서

---

## 기술 스택
**Frontend**: React, CSS  
**Backend**: Spring Boot, FastAPI, MySQL  
**Data/ML**: scikit-learn, Konlpy, BeautifulSoup, pandas  
**API**: 국립중앙도서관, 알라딘  
**Collab**: GitHub, Notion, Swagger

---

## 아키텍처
```mermaid
flowchart LR
    subgraph News
      A[크롤러(BeautifulSoup)] --> B[전처리(Konlpy, 불용어)]
    end

    B --> C[K-Means 클러스터링]
    C --> D[키워드/이슈 벡터]

    D -->|연관 검색어| E[국립중앙도서관 API]
    D -->|매칭| F[알라딘 API]
    E --> G[(MySQL: books)]
    F --> H[(MySQL: stock)]

    subgraph Backend
      I[FastAPI - data-svc] --> C
      J[Spring Boot - api-gw] --> G
      J --> H
    end

    subgraph Frontend
      K[React SPA]
    end

    J <--> K
