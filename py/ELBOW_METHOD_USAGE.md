# 엘보우 기법을 사용한 클러스터링 사용법

## 개요
이 프로젝트에 엘보우 기법(Elbow Method)을 사용한 클러스터링 기능이 추가되었습니다. 엘보우 기법은 K-means 클러스터링에서 최적의 클러스터 수를 찾는 방법입니다.

## 주요 기능

### 1. 엘보우 기법으로 최적 클러스터 수 찾기
- **Inertia 기반 엘보우 포인트**: 클러스터 내 제곱합의 변화율이 급격히 감소하는 지점을 찾습니다.
- **실루엣 점수**: 클러스터 품질을 평가하여 최적 클러스터 수를 결정합니다.
- **2차 미분 기법**: 더 정확한 엘보우 포인트를 찾기 위해 2차 미분을 사용합니다.

### 2. 시각화 기능
- **엘보우 그래프**: Inertia와 클러스터 수의 관계를 시각화
- **실루엣 점수 그래프**: 클러스터 품질을 시각화
- **클러스터 시각화**: t-SNE를 사용한 2D 클러스터 시각화

## 사용 방법

### 1. Python 코드에서 직접 사용

```python
from app.services.nlp import Nlp

# NLP 객체 생성 및 모델 로드
nlp = Nlp()
nlp.LoadModel()

# 엘보우 기법을 사용한 클러스터링
reduced_vectors, labels, cluster_groups = nlp.find_clusters_with_elbow(
    word_list=None,  # None이면 상위 1000개 단어 사용
    max_clusters=20,  # 최대 클러스터 수
    method='kmeans'   # 클러스터링 방법: kmeans, dbscan, agglomerative
)

# 결과 확인
print(f"생성된 클러스터 수: {len(cluster_groups)}")
for cluster_id, words in cluster_groups.items():
    print(f"클러스터 {cluster_id}: {len(words)}개 단어")
```

### 2. 엘보우 그래프만 생성

```python
# 엘보우 그래프 생성
optimal_clusters, inertias, silhouette_scores, cluster_range = nlp.plot_elbow_method(
    word_vectors,  # 단어 벡터 배열
    max_clusters=20,
    save_path="elbow_plot.png"  # 그래프 저장 경로 (선택사항)
)
```

### 3. 기존 시각화 함수에 엘보우 기법 통합

```python
# 엘보우 기법을 사용한 시각화
nlp.VisualizeModel(
    word_list=None,
    num_clusters=None,  # None이면 엘보우 기법으로 자동 결정
    method='kmeans',
    use_elbow=True,      # 엘보우 기법 사용 여부
    show_elbow_plot=True # 엘보우 그래프 표시 여부
)
```

### 4. 테스트 스크립트 실행

```bash
cd py
python test_elbow_method.py
```

테스트 스크립트에서는 다음 옵션을 선택할 수 있습니다:
- **1**: 전체 엘보우 기법 테스트 (클러스터링 + 그래프)
- **2**: 엘보우 그래프만 테스트

## API 엔드포인트

### 1. 엘보우 기법을 사용한 클러스터링
```
GET /clusters/elbow?max_clusters=20&method=kmeans&word_count=500
```

**파라미터:**
- `max_clusters`: 최대 클러스터 수 (기본값: 20, 범위: 2-50)
- `method`: 클러스터링 방법 (kmeans, dbscan, agglomerative)
- `word_count`: 분석할 단어 수 (기본값: 500, 범위: 10-2000)

**응답 예시:**
```json
{
  "success": true,
  "message": "✅ 5개의 클러스터가 생성되었습니다.",
  "total_clusters": 5,
  "total_words": 500,
  "method": "kmeans",
  "clusters": [
    {
      "cluster_id": 0,
      "word_count": 120,
      "words": ["경제", "금리", "주식", "투자", "..."],
      "total_words": 120
    }
  ]
}
```

### 2. 엘보우 그래프 생성
```
GET /clusters/elbow/plot?max_clusters=20&word_count=300
```

**파라미터:**
- `max_clusters`: 최대 클러스터 수 (기본값: 20, 범위: 2-50)
- `word_count`: 분석할 단어 수 (기본값: 300, 범위: 10-1000)

**응답 예시:**
```json
{
  "success": true,
  "message": "✅ 엘보우 그래프가 생성되었습니다.",
  "optimal_clusters": 5,
  "inertias": [1200.5, 800.2, 600.1, 450.3, 380.7],
  "silhouette_scores": [0.0, 0.45, 0.52, 0.48, 0.41],
  "cluster_range": [1, 2, 3, 4, 5],
  "plot_saved": "elbow_plot.png"
}
```

## 엘보우 기법의 원리

### 1. Inertia (클러스터 내 제곱합)
- 각 클러스터의 중심점에서 데이터 포인트까지의 거리의 제곱합
- 클러스터 수가 증가할수록 감소
- 엘보우 포인트에서 감소율이 급격히 둔화

### 2. 실루엣 점수 (Silhouette Score)
- 클러스터 내 응집도와 클러스터 간 분리도를 종합 평가
- -1 ~ 1 범위 (1에 가까울수록 좋음)
- 최적 클러스터 수 결정에 사용

### 3. 2차 미분 기법
- Inertia의 2차 미분이 가장 큰 지점을 엘보우 포인트로 선택
- 더 정확한 엘보우 포인트 탐지

## 주의사항

1. **데이터 크기**: 단어 수가 너무 적으면 엘보우 기법이 제대로 작동하지 않을 수 있습니다.
2. **모델 로드**: 사용 전에 Word2Vec 모델이 로드되어 있어야 합니다.
3. **메모리 사용량**: 단어 수가 많을수록 메모리 사용량이 증가합니다.
4. **실행 시간**: 클러스터 수가 많을수록 실행 시간이 길어집니다.

## 예제 결과

```
🔍 엘보우 기법으로 최적 클러스터 수를 찾는 중...
📊 엘보우 기법 결과: 5개 클러스터
📊 실루엣 점수 기반: 6개 클러스터
📊 최고 실루엣 점수: 0.5234
✅ 총 5개의 클러스터가 생성되었습니다.

📌 클러스터 0: 120개 단어
   대표 단어들: 경제, 금리, 주식, 투자, 시장... (총 120개)

📌 클러스터 1: 95개 단어
   대표 단어들: 정치, 정부, 국회, 선거, 정책... (총 95개)

📌 클러스터 2: 88개 단어
   대표 단어들: 스포츠, 축구, 야구, 경기, 선수... (총 88개)
```

이제 엘보우 기법을 사용하여 더 정확하고 의미 있는 클러스터링을 수행할 수 있습니다!
