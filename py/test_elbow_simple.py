#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
엘보우 기법 간단 테스트 스크립트 (데이터베이스 연결 없이)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

def create_sample_data():
    """샘플 데이터 생성"""
    print("📊 샘플 데이터를 생성합니다...")
    
    # 랜덤 데이터 생성 (3개의 클러스터)
    np.random.seed(42)
    
    # 클러스터 1: 중심 (0, 0)
    cluster1 = np.random.normal(0, 1, (50, 2))
    
    # 클러스터 2: 중심 (5, 5)
    cluster2 = np.random.normal(5, 1, (50, 2))
    
    # 클러스터 3: 중심 (-3, 4)
    cluster3 = np.random.normal([-3, 4], 1, (50, 2))
    
    # 데이터 합치기
    data = np.vstack([cluster1, cluster2, cluster3])
    
    print(f"✅ {len(data)}개의 데이터 포인트 생성 완료")
    return data

def find_optimal_clusters_elbow(data, max_clusters=10):
    """엘보우 기법을 사용한 최적 클러스터 수 찾기"""
    print("🔍 엘보우 기법으로 최적 클러스터 수를 찾는 중...")
    
    cluster_range = range(1, min(max_clusters + 1, len(data)))
    inertias = []
    silhouette_scores = []
    
    for n_clusters in cluster_range:
        if n_clusters == 1:
            # 클러스터가 1개일 때는 inertia 계산
            inertia = np.sum([np.sum((data - np.mean(data, axis=0))**2)])
            inertias.append(inertia)
            silhouette_scores.append(0)
        else:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(data)
            inertias.append(kmeans.inertia_)
            
            if len(set(labels)) > 1:
                silhouette_scores.append(silhouette_score(data, labels))
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

def plot_elbow_method(data, max_clusters=10):
    """엘보우 기법 시각화"""
    optimal_clusters, inertias, silhouette_scores, cluster_range = find_optimal_clusters_elbow(data, max_clusters)
    
    # 그래프 설정
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    # 서브플롯 생성
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 엘보우 그래프 (Inertia)
    ax1.plot(cluster_range, inertias, 'bo-', linewidth=2, markersize=8)
    ax1.axvline(x=optimal_clusters, color='red', linestyle='--', linewidth=2, 
               label=f'Optimal clusters: {optimal_clusters}')
    ax1.set_xlabel('Number of Clusters', fontsize=12)
    ax1.set_ylabel('Inertia (Within-Cluster Sum of Squares)', fontsize=12)
    ax1.set_title('Elbow Method', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 실루엣 점수 그래프
    if len(silhouette_scores) > 1:
        ax2.plot(cluster_range[1:], silhouette_scores[1:], 'go-', linewidth=2, markersize=8)
        silhouette_optimal = cluster_range[np.argmax(silhouette_scores[1:]) + 1]
        ax2.axvline(x=silhouette_optimal, color='red', linestyle='--', linewidth=2,
                   label=f'Optimal clusters: {silhouette_optimal}')
        ax2.set_xlabel('Number of Clusters', fontsize=12)
        ax2.set_ylabel('Silhouette Score', fontsize=12)
        ax2.set_title('Silhouette Score', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
    else:
        ax2.text(0.5, 0.5, 'Insufficient data\n(Need at least 2 clusters)', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
        ax2.set_title('Silhouette Score (Insufficient Data)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # 그래프 저장
    plt.savefig("elbow_test_result.png", dpi=300, bbox_inches='tight')
    print("📊 엘보우 그래프가 저장되었습니다: elbow_test_result.png")
    
    # 그래프 표시 (선택사항)
    try:
        plt.show()
    except KeyboardInterrupt:
        print("📊 그래프 표시를 건너뜁니다.")
    
    return optimal_clusters, inertias, silhouette_scores, cluster_range

def test_clustering(data, n_clusters):
    """클러스터링 테스트"""
    print(f"🔍 {n_clusters}개 클러스터로 클러스터링을 실행합니다...")
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(data)
    
    # 클러스터 품질 평가
    if len(set(labels)) > 1:
        silhouette_avg = silhouette_score(data, labels)
        print(f"📊 클러스터 품질 - 실루엣 점수: {silhouette_avg:.4f}")
    
    # 클러스터별 데이터 개수
    unique_labels = np.unique(labels)
    print(f"✅ 총 {len(unique_labels)}개의 클러스터가 생성되었습니다.")
    
    for cluster_id in unique_labels:
        cluster_data = data[labels == cluster_id]
        print(f"📌 클러스터 {cluster_id}: {len(cluster_data)}개 데이터 포인트")
    
    return labels

def main():
    """메인 함수"""
    print("=" * 60)
    print("🔬 엘보우 기법 간단 테스트 프로그램")
    print("=" * 60)
    print()
    
    # 샘플 데이터 생성
    data = create_sample_data()
    
    # 엘보우 기법으로 최적 클러스터 수 찾기
    optimal_clusters, inertias, silhouette_scores, cluster_range = plot_elbow_method(data, max_clusters=8)
    
    # 클러스터링 실행
    labels = test_clustering(data, optimal_clusters)
    
    print()
    print("=" * 60)
    print("🎉 엘보우 기법 테스트가 성공적으로 완료되었습니다!")
    print(f"📊 최적 클러스터 수: {optimal_clusters}")
    print("=" * 60)

if __name__ == "__main__":
    main()
