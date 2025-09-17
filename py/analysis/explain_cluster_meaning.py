#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
클러스터 개수의 의미 분석 및 시각화
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
from gensim.models import Word2Vec
import platform
from collections import Counter

def load_word2vec_model():
    """Word2Vec 모델 로드"""
    try:
        model_path = "word2vec.model"
        if os.path.exists(model_path):
            model = Word2Vec.load(model_path)
            print(f"✅ Word2Vec 모델이 성공적으로 로드되었습니다.")
            print(f"📊 모델 어휘 크기: {len(model.wv.key_to_index)}")
            return model
        else:
            print("❌ word2vec.model 파일이 없습니다.")
            return None
    except Exception as e:
        print(f"❌ 모델 로딩 중 오류: {e}")
        return None

def get_word_vectors(model, max_words=500):
    """단어 벡터 추출"""
    word_list = list(model.wv.key_to_index)[:max_words]
    valid_words = [word for word in word_list if word in model.wv]
    word_vectors = np.array([model.wv[word] for word in valid_words])
    
    print(f"📊 {len(valid_words)}개의 단어 벡터를 추출했습니다.")
    return valid_words, word_vectors

def analyze_cluster_meaning(words, word_vectors, k_values=[2, 3, 4, 5]):
    """클러스터 개수별 의미 분석"""
    print("🔍 클러스터 개수별 의미 분석을 수행합니다...")
    print("=" * 80)
    
    # 차원 축소
    pca = PCA(n_components=min(50, len(word_vectors[0])))
    word_vectors_pca = pca.fit_transform(word_vectors)
    
    tsne = TSNE(
        n_components=2,
        perplexity=min(30, len(word_vectors) - 1),
        learning_rate=200,
        n_iter=1000,
        random_state=42,
        init='pca'
    )
    reduced_vectors = tsne.fit_transform(word_vectors_pca)
    
    # 그래프 설정
    if platform.system() == "Windows":
        plt.rcParams['font.family'] = 'Malgun Gothic'
    else:
        plt.rcParams['font.family'] = 'Nanum Gothic'
    
    # 각 K 값에 대한 분석
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.ravel()
    
    for i, k in enumerate(k_values):
        # K-means 클러스터링
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(reduced_vectors)
        
        # 실루엣 점수 계산
        silhouette_avg = silhouette_score(reduced_vectors, labels)
        
        # 클러스터별 단어 분석
        cluster_analysis = analyze_clusters_by_k(words, labels, k)
        
        # 시각화
        colors = plt.cm.tab10(np.linspace(0, 1, k))
        for cluster_id in range(k):
            cluster_mask = labels == cluster_id
            axes[i].scatter(reduced_vectors[cluster_mask, 0], 
                          reduced_vectors[cluster_mask, 1], 
                          c=[colors[cluster_id]], 
                          alpha=0.7, s=50, 
                          label=f'클러스터 {cluster_id}')
        
        axes[i].set_title(f'K={k} 클러스터\n실루엣 점수: {silhouette_avg:.3f}', 
                         fontsize=14, fontweight='bold')
        axes[i].set_xlabel('t-SNE-1', fontsize=12)
        axes[i].set_ylabel('t-SNE-2', fontsize=12)
        axes[i].grid(True, alpha=0.3)
        axes[i].legend()
        
        # 클러스터 분석 결과 출력
        print_cluster_analysis(k, cluster_analysis, silhouette_avg)
    
    plt.tight_layout()
    plt.savefig("cluster_meaning_analysis.png", dpi=300, bbox_inches='tight')
    print("📊 클러스터 의미 분석 그래프가 저장되었습니다: cluster_meaning_analysis.png")
    plt.show()

def analyze_clusters_by_k(words, labels, k):
    """K개 클러스터에 대한 상세 분석"""
    cluster_groups = {}
    for i, (word, label) in enumerate(zip(words, labels)):
        if label not in cluster_groups:
            cluster_groups[label] = []
        cluster_groups[label].append(word)
    
    # 각 클러스터의 특성 분석
    cluster_analysis = {}
    for cluster_id, cluster_words in cluster_groups.items():
        # 단어 길이 분석
        word_lengths = [len(word) for word in cluster_words]
        avg_length = np.mean(word_lengths)
        
        # 숫자 포함 단어 비율
        numeric_words = [word for word in cluster_words if any(c.isdigit() for c in word)]
        numeric_ratio = len(numeric_words) / len(cluster_words)
        
        # 복합어 비율 (하이픈, 언더스코어 포함)
        compound_words = [word for word in cluster_words if '-' in word or '_' in word]
        compound_ratio = len(compound_words) / len(cluster_words)
        
        # 영어 포함 단어 비율
        english_words = [word for word in cluster_words if any(c.isascii() and c.isalpha() for c in word)]
        english_ratio = len(english_words) / len(cluster_words)
        
        cluster_analysis[cluster_id] = {
            'words': cluster_words,
            'count': len(cluster_words),
            'avg_length': avg_length,
            'numeric_ratio': numeric_ratio,
            'compound_ratio': compound_ratio,
            'english_ratio': english_ratio,
            'representative_words': cluster_words[:10]  # 대표 단어 10개
        }
    
    return cluster_analysis

def print_cluster_analysis(k, cluster_analysis, silhouette_avg):
    """클러스터 분석 결과 출력"""
    print(f"\n🔸 K={k} 클러스터 분석 (실루엣 점수: {silhouette_avg:.3f})")
    print("-" * 60)
    
    for cluster_id in sorted(cluster_analysis.keys()):
        analysis = cluster_analysis[cluster_id]
        print(f"\n📌 클러스터 {cluster_id} ({analysis['count']}개 단어):")
        print(f"   평균 단어 길이: {analysis['avg_length']:.1f}")
        print(f"   숫자 포함 비율: {analysis['numeric_ratio']:.1%}")
        print(f"   복합어 비율: {analysis['compound_ratio']:.1%}")
        print(f"   영어 포함 비율: {analysis['english_ratio']:.1%}")
        print(f"   대표 단어: {', '.join(analysis['representative_words'])}")
        
        # 클러스터 특성 해석
        characteristics = []
        if analysis['avg_length'] > 4:
            characteristics.append("긴 단어")
        if analysis['numeric_ratio'] > 0.3:
            characteristics.append("숫자 포함")
        if analysis['compound_ratio'] > 0.2:
            characteristics.append("복합어")
        if analysis['english_ratio'] > 0.3:
            characteristics.append("영어 포함")
        
        if characteristics:
            print(f"   특성: {', '.join(characteristics)}")
        else:
            print(f"   특성: 기본 어휘")

def explain_cluster_meaning():
    """클러스터 개수의 의미 설명"""
    print("\n" + "=" * 80)
    print("📚 클러스터 개수의 의미")
    print("=" * 80)
    
    explanations = {
        2: {
            "title": "K=2: 이분법적 분류",
            "meaning": "데이터를 크게 2개의 그룹으로 나눔",
            "examples": [
                "• 기본 어휘 vs 전문 용어",
                "• 일반적 개념 vs 구체적 개념", 
                "• 추상적 vs 구체적",
                "• 단순한 vs 복잡한"
            ],
            "when_to_use": "데이터가 명확히 2개의 다른 성격을 가질 때",
            "pros": ["해석이 간단", "명확한 구분", "안정적인 결과"],
            "cons": ["너무 단순할 수 있음", "세부 구분 부족"]
        },
        3: {
            "title": "K=3: 삼분법적 분류",
            "meaning": "데이터를 3개의 의미적 그룹으로 나눔",
            "examples": [
                "• 기본 어휘 vs 전문 용어 vs 추상적 개념",
                "• 과거 vs 현재 vs 미래",
                "• 긍정적 vs 중립적 vs 부정적",
                "• 개인적 vs 사회적 vs 전문적"
            ],
            "when_to_use": "데이터가 3개의 명확한 카테고리를 가질 때",
            "pros": ["적당한 세분화", "해석 가능", "균형잡힌 분류"],
            "cons": ["과도한 분류 가능성", "해석 복잡성 증가"]
        },
        4: {
            "title": "K=4: 사분법적 분류",
            "meaning": "데이터를 4개의 세분화된 그룹으로 나눔",
            "examples": [
                "• 기본 어휘 vs 전문 용어 vs 추상적 개념 vs 구체적 개념",
                "• 동사 vs 명사 vs 형용사 vs 부사",
                "• 개인적 vs 사회적 vs 전문적 vs 학문적",
                "• 단순한 vs 복잡한 vs 추상적 vs 구체적"
            ],
            "when_to_use": "데이터가 4개의 명확한 하위 그룹을 가질 때",
            "pros": ["세밀한 분류", "상세한 분석 가능"],
            "cons": ["해석 복잡", "과적합 위험", "일부 클러스터가 작을 수 있음"]
        },
        5: {
            "title": "K=5: 오분법적 분류",
            "meaning": "데이터를 5개의 매우 세분화된 그룹으로 나눔",
            "examples": [
                "• 매우 세밀한 의미적 분류",
                "• 복잡한 다차원 분류",
                "• 전문적인 세분화"
            ],
            "when_to_use": "데이터가 매우 복잡하고 세밀한 분류가 필요할 때",
            "pros": ["매우 세밀한 분류", "상세한 분석"],
            "cons": ["해석 매우 복잡", "과적합 위험 높음", "일부 클러스터가 너무 작음"]
        }
    }
    
    for k, explanation in explanations.items():
        print(f"\n{explanation['title']}")
        print("-" * 50)
        print(f"의미: {explanation['meaning']}")
        print(f"예시:")
        for example in explanation['examples']:
            print(f"  {example}")
        print(f"사용 시기: {explanation['when_to_use']}")
        print(f"장점: {', '.join(explanation['pros'])}")
        print(f"단점: {', '.join(explanation['cons'])}")

def main():
    """메인 함수"""
    print("=" * 80)
    print("🔬 클러스터 개수의 의미 분석 프로그램")
    print("=" * 80)
    
    # Word2Vec 모델 로드
    model = load_word2vec_model()
    if model is None:
        return
    
    # 단어 벡터 추출
    words, word_vectors = get_word_vectors(model, max_words=500)
    
    if len(word_vectors) < 10:
        print("❌ 충분한 단어가 없습니다.")
        return
    
    # 클러스터 개수별 의미 분석
    analyze_cluster_meaning(words, word_vectors, k_values=[2, 3, 4, 5])
    
    # 클러스터 개수의 의미 설명
    explain_cluster_meaning()
    
    print("\n" + "=" * 80)
    print("💡 결론:")
    print("=" * 80)
    print("1. K=2: 가장 안정적이고 해석하기 쉬움")
    print("2. K=3: 적당한 세분화, 균형잡힌 분류")
    print("3. K=4: 세밀한 분류, 해석 복잡성 증가")
    print("4. K=5+: 매우 세밀하지만 과적합 위험")
    print("\n🎯 권장사항:")
    print("- 데이터의 성격과 분석 목적에 따라 선택")
    print("- 실루엣 점수와 해석 가능성을 고려")
    print("- K=2 또는 K=3에서 시작하여 점진적으로 증가")
    print("=" * 80)

if __name__ == "__main__":
    main()

