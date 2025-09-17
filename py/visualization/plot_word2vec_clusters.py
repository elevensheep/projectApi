#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word2Vec 모델을 사용한 단어 클러스터링 시각화 스크립트
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
from collections import Counter
import platform

def load_word2vec_model():
    """Word2Vec 모델 로드"""
    try:
        from gensim.models import Word2Vec
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

def get_word_vectors(model, word_list=None, max_words=None):
    """단어 벡터 추출"""
    if word_list is None:
        if max_words is None:
            # 전체 단어 사용
            word_list = list(model.wv.key_to_index)
        else:
            # 상위 빈도 단어들 선택
            word_list = list(model.wv.key_to_index)[:max_words]
    
    # 모델에 존재하는 단어만 필터링
    valid_words = [word for word in word_list if word in model.wv]
    word_vectors = np.array([model.wv[word] for word in valid_words])
    
    print(f"📊 {len(valid_words)}개의 단어 벡터를 추출했습니다.")
    return valid_words, word_vectors

def find_optimal_clusters_elbow(word_vectors, max_clusters=15):
    """엘보우 기법으로 최적 클러스터 수 찾기"""
    print("🔍 엘보우 기법으로 최적 클러스터 수를 찾는 중...")
    
    cluster_range = range(1, min(max_clusters + 1, len(word_vectors)))
    inertias = []
    silhouette_scores = []
    
    for n_clusters in cluster_range:
        if n_clusters == 1:
            inertia = np.sum([np.sum((word_vectors - np.mean(word_vectors, axis=0))**2)])
            inertias.append(inertia)
            silhouette_scores.append(0)
        else:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(word_vectors)
            inertias.append(kmeans.inertia_)
            
            if len(set(labels)) > 1:
                silhouette_scores.append(silhouette_score(word_vectors, labels))
            else:
                silhouette_scores.append(0)
    
    # 엘보우 포인트 찾기
    if len(inertias) > 2:
        first_derivative = np.diff(inertias)
        second_derivative = np.diff(first_derivative)
        
        if len(second_derivative) > 0:
            elbow_idx = np.argmax(second_derivative) + 2
            elbow_clusters = cluster_range[elbow_idx]
        else:
            elbow_clusters = 2
    else:
        elbow_clusters = 2
    
    # 실루엣 점수 기반 최적 클러스터 수
    if len(silhouette_scores) > 1:
        silhouette_optimal = cluster_range[np.argmax(silhouette_scores[1:]) + 1]
    else:
        silhouette_optimal = 2
    
    print(f"📊 엘보우 기법 결과: {elbow_clusters}개 클러스터")
    print(f"📊 실루엣 점수 기반: {silhouette_optimal}개 클러스터")
    print(f"📊 최고 실루엣 점수: {max(silhouette_scores):.4f}")
    
    return elbow_clusters, inertias, silhouette_scores, cluster_range

def plot_elbow_method(inertias, silhouette_scores, cluster_range, optimal_clusters):
    """엘보우 기법 시각화"""
    # 그래프 설정
    if platform.system() == "Windows":
        plt.rcParams['font.family'] = 'Malgun Gothic'
    else:
        plt.rcParams['font.family'] = 'Nanum Gothic'
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 엘보우 그래프
    ax1.plot(cluster_range, inertias, 'bo-', linewidth=2, markersize=8)
    ax1.axvline(x=optimal_clusters, color='red', linestyle='--', linewidth=2, 
               label=f'최적 클러스터 수: {optimal_clusters}')
    ax1.set_xlabel('클러스터 수', fontsize=12)
    ax1.set_ylabel('Inertia (Within-Cluster Sum of Squares)', fontsize=12)
    ax1.set_title('엘보우 기법 (Elbow Method)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 실루엣 점수 그래프
    if len(silhouette_scores) > 1:
        ax2.plot(cluster_range[1:], silhouette_scores[1:], 'go-', linewidth=2, markersize=8)
        silhouette_optimal = cluster_range[np.argmax(silhouette_scores[1:]) + 1]
        ax2.axvline(x=silhouette_optimal, color='red', linestyle='--', linewidth=2,
                   label=f'최적 클러스터 수: {silhouette_optimal}')
        ax2.set_xlabel('클러스터 수', fontsize=12)
        ax2.set_ylabel('Silhouette Score', fontsize=12)
        ax2.set_title('실루엣 점수 (Silhouette Score)', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
    
    plt.tight_layout()
    plt.savefig("word2vec_elbow_analysis.png", dpi=300, bbox_inches='tight')
    print("📊 엘보우 분석 그래프가 저장되었습니다: word2vec_elbow_analysis.png")
    plt.show()

def reduce_dimensions(word_vectors):
    """차원 축소 (PCA + t-SNE)"""
    print("🔍 차원을 축소하는 중...")
    
    # PCA로 먼저 차원 축소
    pca = PCA(n_components=min(50, len(word_vectors[0])))
    word_vectors_pca = pca.fit_transform(word_vectors)
    
    # t-SNE로 2D로 축소
    tsne = TSNE(
        n_components=2,
        perplexity=min(30, len(word_vectors) - 1),
        learning_rate=200,
        n_iter=1000,
        random_state=42,
        init='pca'
    )
    reduced_vectors = tsne.fit_transform(word_vectors_pca)
    
    print("✅ 차원 축소 완료")
    return reduced_vectors

def plot_word_clusters(words, reduced_vectors, labels, optimal_clusters):
    """단어 클러스터 시각화"""
    # 그래프 설정
    if platform.system() == "Windows":
        plt.rcParams['font.family'] = 'Malgun Gothic'
    else:
        plt.rcParams['font.family'] = 'Nanum Gothic'
    
    # 색상 설정
    unique_labels = set(labels)
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))
    color_map = {label: colors[i] for i, label in enumerate(unique_labels)}
    point_colors = [color_map[label] for label in labels]
    
    plt.figure(figsize=(20, 15))
    scatter = plt.scatter(reduced_vectors[:, 0], reduced_vectors[:, 1], 
                         c=point_colors, alpha=0.7, s=50)
    
    # 단어 라벨 표시 (중요한 단어만)
    word_freq = Counter(words)
    important_words = [word for word in words if word_freq[word] > 1 or len(word) > 2]
    
    for i, word in enumerate(words):
        if word in important_words:
            plt.annotate(word, (reduced_vectors[i, 0] + 0.5, reduced_vectors[i, 1] + 0.5), 
                       fontsize=9, alpha=0.8, fontweight='bold')
    
    # 범례
    legend_elements = []
    for label in unique_labels:
        if label != -1:  # DBSCAN의 노이즈 클러스터 제외
            cluster_words = [words[i] for i, l in enumerate(labels) if l == label]
            if cluster_words:
                # 대표 단어 선택 (가장 긴 단어 또는 빈도가 높은 단어)
                representative_word = max(cluster_words, key=lambda w: len(w))
                legend_elements.append(
                    plt.Line2D([0], [0], marker='o', color='w', 
                              markerfacecolor=color_map[label], 
                              markersize=10, label=f"클러스터 {label}: {representative_word}")
                )
    
    plt.legend(handles=legend_elements, title="📌 클러스터 대표 단어", 
              loc="upper left", bbox_to_anchor=(0, 1), fontsize=10)
    
    plt.title(f"Word2Vec 단어 벡터 클러스터링 (K-means, K={optimal_clusters})", fontsize=16)
    plt.xlabel("t-SNE-1", fontsize=12)
    plt.ylabel("t-SNE-2", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("word2vec_clusters.png", dpi=300, bbox_inches='tight')
    print("📊 단어 클러스터 그래프가 저장되었습니다: word2vec_clusters.png")
    plt.show()

def analyze_clusters(words, labels, optimal_clusters):
    """클러스터 분석 및 단어 출력"""
    print(f"\n📊 클러스터 분석 결과 (K={optimal_clusters}):")
    
    # 클러스터별 단어 그룹화
    cluster_groups = {}
    for i, (word, label) in enumerate(zip(words, labels)):
        if label not in cluster_groups:
            cluster_groups[label] = []
        cluster_groups[label].append(word)
    
    # 각 클러스터의 단어들 출력
    for cluster_id in sorted(cluster_groups.keys()):
        cluster_words = cluster_groups[cluster_id]
        print(f"\n🔸 클러스터 {cluster_id} ({len(cluster_words)}개 단어):")
        
        # 단어를 길이와 빈도로 정렬
        sorted_words = sorted(cluster_words, key=lambda w: (len(w), w), reverse=True)
        
        # 단어들을 10개씩 출력
        for i in range(0, len(sorted_words), 10):
            batch = sorted_words[i:i+10]
            print(f"   {', '.join(batch)}")
        
        if len(sorted_words) > 10:
            print(f"   ... (총 {len(sorted_words)}개 단어)")

def main():
    """메인 함수"""
    print("=" * 60)
    print("🔬 Word2Vec 단어 클러스터링 시각화 프로그램")
    print("=" * 60)
    print()
    
    # Word2Vec 모델 로드
    model = load_word2vec_model()
    if model is None:
        print("❌ Word2Vec 모델을 로드할 수 없습니다.")
        return
    
    # 단어 벡터 추출 (더 많은 단어 사용)
    words, word_vectors = get_word_vectors(model, max_words=1000)
    
    if len(word_vectors) < 10:
        print("❌ 충분한 단어가 없습니다. 최소 10개 이상의 단어가 필요합니다.")
        return
    
    # K=30으로 설정 (실루엣 점수 0.5 이상 목표)
    optimal_clusters = 30
    print(f"🎯 실루엣 점수 0.5 이상을 위해 K={optimal_clusters}로 설정합니다.")
    
    # 엘보우 그래프는 생략하고 바로 클러스터링 진행
    print(f"\n📊 K={optimal_clusters} 클러스터링을 진행합니다...")
    
    # 차원 축소
    reduced_vectors = reduce_dimensions(word_vectors)
    
    # K-means 클러스터링
    print(f"\n🔍 {optimal_clusters}개 클러스터로 K-means 클러스터링을 실행합니다...")
    kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(reduced_vectors)
    
    # 클러스터 품질 평가
    if len(set(labels)) > 1:
        silhouette_avg = silhouette_score(reduced_vectors, labels)
        print(f"📊 클러스터 품질 - 실루엣 점수: {silhouette_avg:.4f}")
    
    # 단어 클러스터 시각화
    print("\n📊 단어 클러스터 그래프를 생성합니다...")
    plot_word_clusters(words, reduced_vectors, labels, optimal_clusters)
    
    # 클러스터 분석 및 단어 출력
    analyze_clusters(words, labels, optimal_clusters)
    
    print("\n" + "=" * 60)
    print("🎉 Word2Vec 단어 클러스터링이 완료되었습니다!")
    print("📁 생성된 파일들:")
    print("   - word2vec_elbow_analysis.png (엘보우 분석)")
    print("   - word2vec_clusters.png (단어 클러스터)")
    print("=" * 60)

if __name__ == "__main__":
    main()
