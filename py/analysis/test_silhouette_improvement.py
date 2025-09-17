#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실루엣 점수 개선을 위한 다양한 클러스터링 알고리즘 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, SpectralClustering
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from gensim.models import Word2Vec
import warnings
warnings.filterwarnings('ignore')

def load_word2vec_model():
    """Word2Vec 모델 로드"""
    try:
        model = Word2Vec.load("word2vec.model")
        print(f"✅ Word2Vec 모델이 성공적으로 로드되었습니다.")
        print(f"📊 모델 어휘 크기: {len(model.wv)}")
        return model
    except Exception as e:
        print(f"❌ Word2Vec 모델 로드 실패: {e}")
        return None

def get_word_vectors(model, max_words=1000):
    """단어 벡터 추출"""
    words = list(model.wv.key_to_index.keys())[:max_words]
    word_vectors = np.array([model.wv[word] for word in words])
    return words, word_vectors

def test_clustering_algorithms(word_vectors, words, max_clusters=20):
    """다양한 클러스터링 알고리즘 테스트"""
    
    # 차원 축소 (t-SNE는 너무 느리므로 PCA 사용)
    pca = PCA(n_components=50, random_state=42)
    reduced_vectors = pca.fit_transform(word_vectors)
    
    results = {}
    
    # 1. K-means
    print("\n🔍 K-means 클러스터링 테스트...")
    kmeans_scores = []
    for k in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(reduced_vectors)
        score = silhouette_score(reduced_vectors, labels)
        kmeans_scores.append(score)
        print(f"   K={k}: 실루엣 점수 = {score:.4f}")
    
    results['K-means'] = kmeans_scores
    
    # 2. Agglomerative Clustering
    print("\n🔍 Agglomerative Clustering 테스트...")
    agg_scores = []
    for k in range(2, max_clusters + 1):
        agg = AgglomerativeClustering(n_clusters=k)
        labels = agg.fit_predict(reduced_vectors)
        score = silhouette_score(reduced_vectors, labels)
        agg_scores.append(score)
        print(f"   K={k}: 실루엣 점수 = {score:.4f}")
    
    results['Agglomerative'] = agg_scores
    
    # 3. Spectral Clustering
    print("\n🔍 Spectral Clustering 테스트...")
    spectral_scores = []
    for k in range(2, min(max_clusters + 1, 15)):  # Spectral은 계산이 무거움
        try:
            spectral = SpectralClustering(n_clusters=k, random_state=42)
            labels = spectral.fit_predict(reduced_vectors)
            score = silhouette_score(reduced_vectors, labels)
            spectral_scores.append(score)
            print(f"   K={k}: 실루엣 점수 = {score:.4f}")
        except Exception as e:
            print(f"   K={k}: 오류 발생 - {e}")
            spectral_scores.append(0)
    
    results['Spectral'] = spectral_scores
    
    # 4. DBSCAN (자동 클러스터 수 결정)
    print("\n🔍 DBSCAN 클러스터링 테스트...")
    dbscan_scores = []
    eps_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    
    for eps in eps_values:
        try:
            dbscan = DBSCAN(eps=eps, min_samples=5)
            labels = dbscan.fit_predict(reduced_vectors)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            
            if n_clusters > 1:
                score = silhouette_score(reduced_vectors, labels)
                dbscan_scores.append((eps, n_clusters, score))
                print(f"   eps={eps}, 클러스터={n_clusters}: 실루엣 점수 = {score:.4f}")
            else:
                print(f"   eps={eps}: 클러스터 수 부족")
        except Exception as e:
            print(f"   eps={eps}: 오류 발생 - {e}")
    
    results['DBSCAN'] = dbscan_scores
    
    return results

def plot_silhouette_comparison(results, max_clusters=20):
    """실루엣 점수 비교 그래프"""
    plt.figure(figsize=(15, 10))
    
    # K-means, Agglomerative, Spectral 비교
    plt.subplot(2, 2, 1)
    k_range = range(2, max_clusters + 1)
    plt.plot(k_range, results['K-means'], 'o-', label='K-means', linewidth=2)
    plt.plot(k_range, results['Agglomerative'], 's-', label='Agglomerative', linewidth=2)
    
    if len(results['Spectral']) > 0:
        spectral_range = range(2, 2 + len(results['Spectral']))
        plt.plot(spectral_range, results['Spectral'], '^-', label='Spectral', linewidth=2)
    
    plt.axhline(y=0.5, color='r', linestyle='--', label='목표: 0.5')
    plt.xlabel('클러스터 수 (K)')
    plt.ylabel('실루엣 점수')
    plt.title('클러스터링 알고리즘별 실루엣 점수 비교')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 최고 점수 찾기
    plt.subplot(2, 2, 2)
    max_kmeans = max(results['K-means'])
    max_agg = max(results['Agglomerative'])
    max_spectral = max(results['Spectral']) if results['Spectral'] else 0
    
    algorithms = ['K-means', 'Agglomerative', 'Spectral']
    max_scores = [max_kmeans, max_agg, max_spectral]
    
    bars = plt.bar(algorithms, max_scores, color=['skyblue', 'lightgreen', 'lightcoral'])
    plt.axhline(y=0.5, color='r', linestyle='--', label='목표: 0.5')
    plt.ylabel('최고 실루엣 점수')
    plt.title('알고리즘별 최고 실루엣 점수')
    plt.legend()
    
    # 값 표시
    for bar, score in zip(bars, max_scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{score:.4f}', ha='center', va='bottom')
    
    # DBSCAN 결과
    if results['DBSCAN']:
        plt.subplot(2, 2, 3)
        eps_values = [item[0] for item in results['DBSCAN']]
        dbscan_scores = [item[2] for item in results['DBSCAN']]
        n_clusters = [item[1] for item in results['DBSCAN']]
        
        plt.scatter(eps_values, dbscan_scores, c=n_clusters, cmap='viridis', s=100)
        plt.axhline(y=0.5, color='r', linestyle='--', label='목표: 0.5')
        plt.xlabel('eps 값')
        plt.ylabel('실루엣 점수')
        plt.title('DBSCAN 결과 (색상: 클러스터 수)')
        plt.colorbar(label='클러스터 수')
        plt.legend()
    
    plt.tight_layout()
    plt.savefig('silhouette_comparison.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 실루엣 점수 비교 그래프가 저장되었습니다: silhouette_comparison.png")
    
    return max_scores

def find_best_parameters(results, word_vectors, words):
    """최적 파라미터 찾기"""
    print("\n🎯 최적 파라미터 분석...")
    
    # K-means 최적 K
    kmeans_scores = results['K-means']
    best_k_kmeans = kmeans_scores.index(max(kmeans_scores)) + 2
    print(f"K-means 최적 K: {best_k_kmeans} (실루엣 점수: {max(kmeans_scores):.4f})")
    
    # Agglomerative 최적 K
    agg_scores = results['Agglomerative']
    best_k_agg = agg_scores.index(max(agg_scores)) + 2
    print(f"Agglomerative 최적 K: {best_k_agg} (실루엣 점수: {max(agg_scores):.4f})")
    
    # DBSCAN 최적 파라미터
    if results['DBSCAN']:
        best_dbscan = max(results['DBSCAN'], key=lambda x: x[2])
        print(f"DBSCAN 최적 파라미터: eps={best_dbscan[0]}, 클러스터={best_dbscan[1]} (실루엣 점수: {best_dbscan[2]:.4f})")
    
    return best_k_kmeans, best_k_agg

def main():
    print("=" * 60)
    print("🔬 실루엣 점수 개선을 위한 클러스터링 알고리즘 비교")
    print("=" * 60)
    
    # Word2Vec 모델 로드
    model = load_word2vec_model()
    if model is None:
        return
    
    # 단어 벡터 추출
    words, word_vectors = get_word_vectors(model, max_words=1000)
    print(f"📊 {len(words)}개의 단어 벡터를 추출했습니다.")
    
    # 다양한 클러스터링 알고리즘 테스트
    results = test_clustering_algorithms(word_vectors, words, max_clusters=20)
    
    # 결과 시각화
    max_scores = plot_silhouette_comparison(results, max_clusters=20)
    
    # 최적 파라미터 찾기
    best_k_kmeans, best_k_agg = find_best_parameters(results, word_vectors, words)
    
    # 0.5 이상 달성 여부 확인
    print(f"\n🎯 실루엣 점수 0.5 이상 달성 여부:")
    print(f"K-means 최고 점수: {max(results['K-means']):.4f} {'✅' if max(results['K-means']) >= 0.5 else '❌'}")
    print(f"Agglomerative 최고 점수: {max(results['Agglomerative']):.4f} {'✅' if max(results['Agglomerative']) >= 0.5 else '❌'}")
    
    if results['Spectral']:
        print(f"Spectral 최고 점수: {max(results['Spectral']):.4f} {'✅' if max(results['Spectral']) >= 0.5 else '❌'}")
    
    if results['DBSCAN']:
        best_dbscan_score = max(results['DBSCAN'], key=lambda x: x[2])[2]
        print(f"DBSCAN 최고 점수: {best_dbscan_score:.4f} {'✅' if best_dbscan_score >= 0.5 else '❌'}")
    
    print("\n" + "=" * 60)
    print("🎉 클러스터링 알고리즘 비교 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()

