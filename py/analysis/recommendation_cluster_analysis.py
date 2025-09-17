#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
추천 시스템을 위한 클러스터 분석
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

def get_word_vectors(model, max_words=1000):
    """단어 벡터 추출"""
    word_list = list(model.wv.key_to_index)[:max_words]
    valid_words = [word for word in word_list if word in model.wv]
    word_vectors = np.array([model.wv[word] for word in valid_words])
    
    print(f"📊 {len(valid_words)}개의 단어 벡터를 추출했습니다.")
    return valid_words, word_vectors

def analyze_recommendation_clusters(words, word_vectors, model, k_values=[5, 8, 10, 12, 15]):
    """추천 시스템을 위한 클러스터 분석"""
    print("🔍 추천 시스템을 위한 클러스터 분석을 수행합니다...")
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
    
    # 각 K 값에 대한 분석
    results = {}
    
    for k in k_values:
        print(f"\n🔸 K={k} 클러스터 분석:")
        print("-" * 50)
        
        # K-means 클러스터링
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(reduced_vectors)
        
        # 실루엣 점수 계산
        silhouette_avg = silhouette_score(reduced_vectors, labels)
        
        # 클러스터별 단어 분석
        cluster_groups = {}
        for i, (word, label) in enumerate(zip(words, labels)):
            if label not in cluster_groups:
                cluster_groups[label] = []
            cluster_groups[label].append(word)
        
        # 클러스터 크기 분석
        cluster_sizes = [len(cluster_groups[i]) for i in range(k)]
        avg_cluster_size = np.mean(cluster_sizes)
        min_cluster_size = min(cluster_sizes)
        max_cluster_size = max(cluster_sizes)
        
        # 클러스터 내 유사도 분석
        intra_cluster_similarities = []
        for cluster_id in range(k):
            cluster_words = cluster_groups[cluster_id]
            if len(cluster_words) > 1:
                # 클러스터 내 단어들의 평균 유사도 계산
                similarities = []
                for i, word1 in enumerate(cluster_words):
                    for j, word2 in enumerate(cluster_words[i+1:], i+1):
                        if word1 in model.wv and word2 in model.wv:
                            sim = model.wv.similarity(word1, word2)
                            similarities.append(sim)
                if similarities:
                    intra_cluster_similarities.append(np.mean(similarities))
        
        avg_intra_similarity = np.mean(intra_cluster_similarities) if intra_cluster_similarities else 0
        
        results[k] = {
            'silhouette': silhouette_avg,
            'cluster_sizes': cluster_sizes,
            'avg_cluster_size': avg_cluster_size,
            'min_cluster_size': min_cluster_size,
            'max_cluster_size': max_cluster_size,
            'avg_intra_similarity': avg_intra_similarity,
            'cluster_groups': cluster_groups
        }
        
        print(f"   실루엣 점수: {silhouette_avg:.3f}")
        print(f"   평균 클러스터 크기: {avg_cluster_size:.1f}")
        print(f"   최소 클러스터 크기: {min_cluster_size}")
        print(f"   최대 클러스터 크기: {max_cluster_size}")
        print(f"   클러스터 내 평균 유사도: {avg_intra_similarity:.3f}")
        
        # 각 클러스터의 대표 단어 출력
        print(f"   클러스터별 대표 단어:")
        for cluster_id in range(min(3, k)):  # 처음 3개 클러스터만 출력
            cluster_words = cluster_groups[cluster_id]
            representative_words = cluster_words[:8]  # 처음 8개 단어
            print(f"     클러스터 {cluster_id}: {', '.join(representative_words)}")
    
    return results, reduced_vectors

def plot_recommendation_clusters(words, reduced_vectors, k_values=[5, 8, 10, 12, 15]):
    """추천 시스템용 클러스터 시각화"""
    # 그래프 설정
    if platform.system() == "Windows":
        plt.rcParams['font.family'] = 'Malgun Gothic'
    else:
        plt.rcParams['font.family'] = 'Nanum Gothic'
    
    fig, axes = plt.subplots(2, 3, figsize=(24, 16))
    axes = axes.ravel()
    
    for i, k in enumerate(k_values):
        # K-means 클러스터링
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(reduced_vectors)
        
        # 실루엣 점수 계산
        silhouette_avg = silhouette_score(reduced_vectors, labels)
        
        # 시각화
        colors = plt.cm.tab20(np.linspace(0, 1, k))
        for cluster_id in range(k):
            cluster_mask = labels == cluster_id
            axes[i].scatter(reduced_vectors[cluster_mask, 0], 
                          reduced_vectors[cluster_mask, 1], 
                          c=[colors[cluster_id]], 
                          alpha=0.7, s=30, 
                          label=f'C{cluster_id}')
        
        axes[i].set_title(f'K={k} 클러스터\n실루엣: {silhouette_avg:.3f}', 
                         fontsize=12, fontweight='bold')
        axes[i].set_xlabel('t-SNE-1', fontsize=10)
        axes[i].set_ylabel('t-SNE-2', fontsize=10)
        axes[i].grid(True, alpha=0.3)
        if k <= 10:  # 클러스터가 많으면 범례 생략
            axes[i].legend(fontsize=8)
    
    # 마지막 subplot 제거
    axes[-1].remove()
    
    plt.tight_layout()
    plt.savefig("recommendation_clusters.png", dpi=300, bbox_inches='tight')
    print("📊 추천 시스템용 클러스터 그래프가 저장되었습니다: recommendation_clusters.png")
    plt.show()

def recommend_optimal_k_for_recommendation(results):
    """추천 시스템에 최적인 K 값 추천"""
    print("\n" + "=" * 80)
    print("🎯 추천 시스템을 위한 최적 K 값 분석")
    print("=" * 80)
    
    # 추천 시스템에 중요한 요소들
    print("\n📊 추천 시스템 평가 기준:")
    print("1. 실루엣 점수 (클러스터 품질)")
    print("2. 클러스터 크기 균형 (너무 작거나 크지 않음)")
    print("3. 클러스터 내 유사도 (관련 단어들이 함께 그룹화)")
    print("4. 클러스터 개수 (적당한 세분화)")
    
    print("\n📈 각 K 값별 평가:")
    print("-" * 60)
    
    scores = {}
    for k, result in results.items():
        # 점수 계산 (0-1 범위로 정규화)
        silhouette_score = result['silhouette']
        
        # 클러스터 크기 균형 점수 (표준편차가 작을수록 좋음)
        size_std = np.std(result['cluster_sizes'])
        size_balance_score = 1 / (1 + size_std / result['avg_cluster_size'])
        
        # 클러스터 내 유사도 점수
        similarity_score = result['avg_intra_similarity']
        
        # 클러스터 개수 점수 (5-15 범위에서 적당)
        if 5 <= k <= 15:
            count_score = 1 - abs(k - 10) / 10
        else:
            count_score = 0.5
        
        # 종합 점수 (가중평균)
        total_score = (silhouette_score * 0.3 + 
                      size_balance_score * 0.2 + 
                      similarity_score * 0.3 + 
                      count_score * 0.2)
        
        scores[k] = {
            'total': total_score,
            'silhouette': silhouette_score,
            'size_balance': size_balance_score,
            'similarity': similarity_score,
            'count': count_score
        }
        
        print(f"K={k:2d}: 총점={total_score:.3f} (실루엣={silhouette_score:.3f}, "
              f"크기균형={size_balance_score:.3f}, 유사도={similarity_score:.3f}, "
              f"개수={count_score:.3f})")
    
    # 최적 K 값 찾기
    best_k = max(scores.keys(), key=lambda k: scores[k]['total'])
    best_score = scores[best_k]['total']
    
    print(f"\n🏆 추천 시스템에 최적인 K 값: {best_k}")
    print(f"   종합 점수: {best_score:.3f}")
    
    print(f"\n💡 K={best_k}를 선택하는 이유:")
    print(f"   - 실루엣 점수: {scores[best_k]['silhouette']:.3f} (클러스터 품질)")
    print(f"   - 크기 균형: {scores[best_k]['size_balance']:.3f} (균등한 분포)")
    print(f"   - 내부 유사도: {scores[best_k]['similarity']:.3f} (관련 단어 그룹화)")
    print(f"   - 클러스터 개수: {scores[best_k]['count']:.3f} (적당한 세분화)")
    
    return best_k, scores

def main():
    """메인 함수"""
    print("=" * 80)
    print("🔬 추천 시스템을 위한 클러스터 분석 프로그램")
    print("=" * 80)
    
    # Word2Vec 모델 로드
    model = load_word2vec_model()
    if model is None:
        return
    
    # 단어 벡터 추출
    words, word_vectors = get_word_vectors(model, max_words=1000)
    
    if len(word_vectors) < 10:
        print("❌ 충분한 단어가 없습니다.")
        return
    
    # 추천 시스템을 위한 클러스터 분석
    results, reduced_vectors = analyze_recommendation_clusters(words, word_vectors, model)
    
    # 클러스터 시각화
    print("\n📊 클러스터 시각화를 생성합니다...")
    plot_recommendation_clusters(words, reduced_vectors)
    
    # 최적 K 값 추천
    best_k, scores = recommend_optimal_k_for_recommendation(results)
    
    print("\n" + "=" * 80)
    print("🎯 결론:")
    print("=" * 80)
    print(f"✅ 추천 시스템에는 K={best_k}가 가장 적합합니다!")
    print(f"   - 관련성이 높은 단어들이 함께 그룹화됩니다")
    print(f"   - 적당한 세분화로 정확한 추천이 가능합니다")
    print(f"   - 클러스터 크기가 균형잡혀 있습니다")
    print("\n💡 K=2는 추천 시스템에 부적합합니다:")
    print("   - 너무 단순한 분류로 세밀한 추천 불가")
    print("   - 관련 단어들을 세밀하게 구분할 수 없음")
    print("   - 추천 정확도가 떨어짐")
    print("=" * 80)

if __name__ == "__main__":
    main()
