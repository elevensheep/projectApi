# 프로젝트 폴더 구조 정리 제안

## 현재 상황
`py` 폴더에 모든 파일들이 평면적으로 배치되어 있어 관리가 어려운 상태입니다.

## 제안하는 새로운 폴더 구조

```
py/
├── analysis/                    # 분석 스크립트
│   ├── analyze_optimal_clusters.py
│   ├── explain_cluster_meaning.py
│   ├── recommendation_cluster_analysis.py
│   └── test_silhouette_improvement.py
│
├── visualization/               # 시각화 스크립트
│   ├── plot_kmeans_clusters.py
│   └── plot_word2vec_clusters.py
│
├── tests/                       # 테스트 스크립트
│   ├── test_elbow_method.py
│   └── test_elbow_simple.py
│
├── setup/                       # 설치 및 설정
│   ├── install_requirements.bat
│   ├── install_requirements.ps1
│   ├── requirements.txt
│   └── requirements_clean.txt
│
├── docs/                        # 문서
│   ├── ELBOW_METHOD_USAGE.md
│   ├── INSTALLATION_GUIDE.md
│   └── FOLDER_STRUCTURE_PROPOSAL.md
│
├── results/                     # 생성된 결과물
│   ├── images/                  # 분석 결과 이미지
│   │   ├── cluster_meaning_analysis.png
│   │   ├── comprehensive_cluster_analysis.png
│   │   ├── elbow_test_result.png
│   │   ├── kmeans_clusters_comparison.png
│   │   ├── kmeans_elbow_analysis.png
│   │   ├── kmeans_optimal_clusters.png
│   │   ├── recommendation_clusters.png
│   │   ├── silhouette_comparison.png
│   │   ├── word2vec_clusters.png
│   │   └── word2vec_elbow_analysis.png
│   └── data/                    # 생성된 데이터 (향후)
│
├── app/                         # 기존 앱 코드 (유지)
│
└── README.md                    # 메인 README
```

## 정리 작업 계획

1. **폴더 생성**: 필요한 폴더들 생성
2. **파일 이동**: 파일들을 적절한 폴더로 이동
3. **import 경로 수정**: 스크립트들의 import 경로 수정
4. **문서 업데이트**: README 및 설치 가이드 업데이트
5. **정리**: 중복 파일 제거

## 장점

- **명확한 구조**: 각 파일의 역할이 폴더명으로 명확해짐
- **쉬운 관리**: 관련 파일들이 그룹화되어 관리 용이
- **확장성**: 새로운 기능 추가 시 적절한 폴더에 배치 가능
- **가독성**: 프로젝트 구조를 한눈에 파악 가능
