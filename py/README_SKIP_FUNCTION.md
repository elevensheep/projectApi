# 건너뛰기 기능 사용법

## 개요
오늘자 데이터가 이미 존재하는 경우 중복 처리를 방지하기 위한 건너뛰기 기능이 구현되었습니다.

## 기능 설명

### 1. 자동 건너뛰기 체크
- **기준값**: 뉴스 키워드 10개 이상, 추천 도서 50권 이상
- **동작**: 오늘자 데이터가 기준값을 충족하면 처리를 건너뜀
- **적용 위치**: 
  - FastAPI 서버 시작 시 (`main.py`)
  - GPU 추천 시스템 실행 시 (`bert_recommendation_gpu.py`)

### 2. 수동 건너뛰기 체크
```bash
python check_and_skip_duplicate.py
```
- 현재 데이터 상태를 확인하고 건너뛰기 여부를 결정
- 사용자에게 건너뛰기 또는 강제 재처리 옵션 제공

### 3. 강제 재처리
- 오늘자 데이터를 삭제하고 새로 처리
- `check_and_skip_duplicate.py`에서 옵션 2 선택

## 사용 가능한 스크립트

### 1. 건너뛰기 체크 및 관리
```bash
# 기본 건너뛰기 체크
python check_and_skip_duplicate.py

# 건너뛰기 기능 테스트
python test_skip_function.py
```

### 2. 진행상황 모니터링
```bash
# 일회성 모니터링
python monitor_progress.py

# 지속적 모니터링 (30초마다)
python monitor_progress.py --continuous
```

### 3. 추천 시스템 실행
```bash
# GPU 최적화된 추천 시스템 (건너뛰기 기능 포함)
python app/utils/bert_recommendation_gpu.py

# FastAPI 서버 (건너뛰기 기능 포함)
python app/main.py
```

## 데이터베이스 테이블

### 관련 테이블
- `tb_news_keyword`: 뉴스 키워드 데이터
- `tb_recommend`: 추천 도서 데이터

### 체크 기준
- **날짜**: `news_date` 필드의 오늘 날짜
- **카테고리**: `news_category` 필드 (politics, sports, economic, society, world)
- **수량**: 각 카테고리별 뉴스 키워드 수와 추천 도서 수

## 설정 가능한 임계값

### 기본 임계값
```python
min_news_keywords = 10    # 최소 뉴스 키워드 수
min_recommendations = 50  # 최소 추천 도서 수
```

### 사용자 정의 임계값
```python
# 더 엄격한 조건
checker.should_skip_processing(min_news_keywords=20, min_recommendations=100)

# 더 관대한 조건
checker.should_skip_processing(min_news_keywords=5, min_recommendations=20)
```

## 현재 데이터 상태 (2025-08-08)

| 카테고리 | 뉴스 키워드 | 추천 도서 | 상태 |
|---------|------------|----------|------|
| politics | 26개 | 50권 | ✅ 완료 |
| sports | 10개 | 165권 | ✅ 완료 |
| economic | 10개 | 283권 | ✅ 완료 |
| society | 10개 | 82권 | ✅ 완료 |
| world | 10개 | 110권 | ✅ 완료 |
| **총계** | **66개** | **690권** | **✅ 건너뛰기 대상** |

## 장점

### 1. 시간 절약
- 중복 처리 방지로 불필요한 시간 낭비 방지
- 특히 BERT 모델 처리 시간이 긴 경우 효과적

### 2. 리소스 효율성
- GPU 메모리 및 CPU 사용량 절약
- 데이터베이스 부하 감소

### 3. 안정성
- 이미 완료된 작업의 재실행 방지
- 데이터 일관성 유지

## 주의사항

### 1. 강제 재처리 시
- 오늘자 데이터가 완전히 삭제됨
- 복구 불가능하므로 신중하게 사용

### 2. 임계값 조정
- 너무 낮은 임계값: 불완전한 데이터로 건너뛰기
- 너무 높은 임계값: 완료된 데이터도 재처리

### 3. 날짜 기준
- 한국 시간 기준 오늘 날짜 사용
- 자정 이후 새로운 날짜로 인식

## 문제 해결

### 1. 건너뛰기가 예상과 다를 때
```bash
# 현재 데이터 상태 확인
python test_skip_function.py

# 임계값 조정 테스트
python test_skip_function.py
```

### 2. 강제 재처리가 필요한 경우
```bash
python check_and_skip_duplicate.py
# 옵션 2 선택
```

### 3. 데이터베이스 오류 시
- 데이터베이스 연결 상태 확인
- 테이블 구조 확인 (`tb_news_keyword`, `tb_recommend`)

## 로그 확인

### FastAPI 서버 로그
```
🚀 서버 시작과 함께 추천 시스템 실행 중...
🔍 오늘(2025-08-08) 데이터 확인 결과:
⏭️  오늘자 데이터가 이미 존재하여 처리를 건너뜁니다.
✅ 추천 시스템 초기화 완료 (건너뛰기)
```

### GPU 추천 시스템 로그
```
🚀 GPU 최적화된 BERT 추천 시스템 시작
⏭️  오늘자 데이터가 이미 존재하여 처리를 건너뜁니다.
```

## 향후 개선 사항

1. **웹 인터페이스**: 브라우저에서 건너뛰기 상태 확인
2. **스케줄링**: 자동 실행 시간 설정
3. **알림 기능**: 처리 완료 시 알림
4. **백업 기능**: 삭제 전 데이터 백업
5. **통계 대시보드**: 처리 현황 시각화
