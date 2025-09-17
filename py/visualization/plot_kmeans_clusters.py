"""
K-means 클러스터링 시각화 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score
import seaborn as sns

def create_sample_data():
    """샘플 데이터 생성 (3개의 클러스터)"""
    print("📊 샘플 데이터를 생성합니다...")


    X, y_true = make_blobs(
        n_samples=300, 
        centers=3, 
        cluster_std=1.5, 
        random_state=42
    )
    
    print(f"✅ {len(X)}개의 데이터 포인트 생성 완료")
    print(f"✅ 실제 클러스터 수: {len(np.unique(y_true))}")
    
    return X, y_true

def find_optimal_k(X, max_k=10):
    """최적의 K 값 찾기 (엘보우 기법)"""
    print("🔍 최적의 K 값을 찾는 중...")
    
    inertias = []
    silhouette_scores = []
    k_range = range(1, max_k + 1)
    
    for k in k_range:
        if k == 1:
            # k=1일 때는 inertia만 계산
            inertia = np.sum([np.sum((X - np.mean(X, axis=0))**2)])
            inertias.append(inertia)
            silhouette_scores.append(0)
        else:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            inertias.append(kmeans.inertia_)
            
            if len(set(labels)) > 1:
                silhouette_scores.append(silhouette_score(X, labels))
            else:
                silhouette_scores.append(0)
    
    # 엘보우 포인트 찾기
    if len(inertias) > 2:
        first_derivative = np.diff(inertias)
        second_derivative = np.diff(first_derivative)
        
        if len(second_derivative) > 0:
            elbow_idx = np.argmax(second_derivative) + 2
            optimal_k = k_range[elbow_idx]
        else:
            optimal_k = 2
    else:
        optimal_k = 2
    
    # 실루엣 점수 기반 최적 K
    if len(silhouette_scores) > 1:
        silhouette_optimal = k_range[np.argmax(silhouette_scores[1:]) + 1]
    else:
        silhouette_optimal = 2
    
    print(f"📊 엘보우 기법 결과: {optimal_k}개 클러스터")
    print(f"📊 실루엣 점수 기반: {silhouette_optimal}개 클러스터")
    print(f"📊 최고 실루엣 점수: {max(silhouette_scores):.4f}")
    
    return optimal_k, inertias, silhouette_scores, k_range

def plot_elbow_method(inertias, silhouette_scores, k_range, optimal_k):
    """엘보우 기법 그래프"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 엘보우 그래프
    ax1.plot(k_range, inertias, 'bo-', linewidth=2, markersize=8)
    ax1.axvline(x=optimal_k, color='red', linestyle='--', linewidth=2, 
               label=f'Optimal K: {optimal_k}')
    ax1.set_xlabel('Number of Clusters (K)', fontsize=12)
    ax1.set_ylabel('Inertia (Within-Cluster Sum of Squares)', fontsize=12)
    ax1.set_title('Elbow Method for Optimal K', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 실루엣 점수 그래프
    if len(silhouette_scores) > 1:
        ax2.plot(k_range[1:], silhouette_scores[1:], 'go-', linewidth=2, markersize=8)
        silhouette_optimal = k_range[np.argmax(silhouette_scores[1:]) + 1]
        ax2.axvline(x=silhouette_optimal, color='red', linestyle='--', linewidth=2,
                   label=f'Optimal K: {silhouette_optimal}')
        ax2.set_xlabel('Number of Clusters (K)', fontsize=12)
        ax2.set_ylabel('Silhouette Score', fontsize=12)
        ax2.set_title('Silhouette Score', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
    
    plt.tight_layout()
    plt.savefig("kmeans_elbow_analysis.png", dpi=300, bbox_inches='tight')
    print("📊 엘보우 분석 그래프가 저장되었습니다: kmeans_elbow_analysis.png")
    plt.show()

def plot_kmeans_clusters(X, y_true, k_values=[2, 3, 4, 5]):
    """K-means 클러스터링 결과 시각화"""
    n_plots = len(k_values)
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.ravel()
    
    for i, k in enumerate(k_values):
        # K-means 클러스터링
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        y_pred = kmeans.fit_predict(X)
        
        # 클러스터 중심점
        centers = kmeans.cluster_centers_
        
        # 실루엣 점수 계산
        if len(set(y_pred)) > 1:
            silhouette_avg = silhouette_score(X, y_pred)
        else:
            silhouette_avg = 0
        
        # 그래프 그리기
        scatter = axes[i].scatter(X[:, 0], X[:, 1], c=y_pred, cmap='viridis', 
                                 alpha=0.7, s=50, edgecolors='black', linewidth=0.5)
        
        # 클러스터 중심점 표시
        axes[i].scatter(centers[:, 0], centers[:, 1], c='red', marker='x', 
                       s=200, linewidths=3, label='Centroids')
        
        # 제목 및 라벨
        axes[i].set_title(f'K-means (K={k})\nSilhouette Score: {silhouette_avg:.3f}', 
                         fontsize=12, fontweight='bold')
        axes[i].set_xlabel('Feature 1', fontsize=10)
        axes[i].set_ylabel('Feature 2', fontsize=10)
        axes[i].grid(True, alpha=0.3)
        axes[i].legend()
        
        # 컬러바 추가
        plt.colorbar(scatter, ax=axes[i], shrink=0.8)
    
    plt.tight_layout()
    plt.savefig("kmeans_clusters_comparison.png", dpi=300, bbox_inches='tight')
    print("📊 K-means 클러스터 비교 그래프가 저장되었습니다: kmeans_clusters_comparison.png")
    plt.show()

def plot_cluster_analysis(X, y_true, optimal_k):
    """최적 K로 클러스터 분석"""
    # K-means 클러스터링
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    y_pred = kmeans.fit_predict(X)
    
    # 실루엣 점수 계산
    silhouette_avg = silhouette_score(X, y_pred)
    
    # 그래프 생성
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 실제 클러스터 vs 예측 클러스터
    scatter1 = ax1.scatter(X[:, 0], X[:, 1], c=y_true, cmap='viridis', 
                          alpha=0.7, s=50, edgecolors='black', linewidth=0.5)
    ax1.set_title('True Clusters', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Feature 1', fontsize=12)
    ax1.set_ylabel('Feature 2', fontsize=12)
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter1, ax=ax1, shrink=0.8)
    
    scatter2 = ax2.scatter(X[:, 0], X[:, 1], c=y_pred, cmap='viridis', 
                          alpha=0.7, s=50, edgecolors='black', linewidth=0.5)
    
    # 클러스터 중심점 표시
    centers = kmeans.cluster_centers_
    ax2.scatter(centers[:, 0], centers[:, 1], c='red', marker='x', 
               s=200, linewidths=3, label='Centroids')
    
    ax2.set_title(f'K-means Clusters (K={optimal_k})\nSilhouette Score: {silhouette_avg:.3f}', 
                 fontsize=14, fontweight='bold')
    ax2.set_xlabel('Feature 1', fontsize=12)
    ax2.set_ylabel('Feature 2', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    plt.colorbar(scatter2, ax=ax2, shrink=0.8)
    
    plt.tight_layout()
    plt.savefig("kmeans_optimal_clusters.png", dpi=300, bbox_inches='tight')
    print("📊 최적 K-means 클러스터 그래프가 저장되었습니다: kmeans_optimal_clusters.png")
    plt.show()
    
    # 클러스터 통계 출력
    print(f"\n📊 클러스터 분석 결과 (K={optimal_k}):")
    print(f"   실루엣 점수: {silhouette_avg:.4f}")
    print(f"   클러스터 중심점:")
    for i, center in enumerate(centers):
        print(f"     클러스터 {i}: ({center[0]:.2f}, {center[1]:.2f})")
    
    # 각 클러스터의 데이터 개수
    unique_labels = np.unique(y_pred)
    print(f"   클러스터별 데이터 개수:")
    for cluster_id in unique_labels:
        count = np.sum(y_pred == cluster_id)
        print(f"     클러스터 {cluster_id}: {count}개")

def main():
    """메인 함수"""
    print("=" * 60)
    print("🔬 K-means 클러스터링 시각화 프로그램")
    print("=" * 60)
    print()
    
    # 샘플 데이터 생성
    X, y_true = create_sample_data()
    
    # 최적 K 값 찾기
    optimal_k, inertias, silhouette_scores, k_range = find_optimal_k(X, max_k=8)
    
    # 엘보우 기법 그래프
    print("\n📊 엘보우 기법 분석 그래프를 생성합니다...")
    plot_elbow_method(inertias, silhouette_scores, k_range, optimal_k)
    
    # 다양한 K 값으로 클러스터 비교
    print("\n📊 다양한 K 값으로 클러스터 비교 그래프를 생성합니다...")
    plot_kmeans_clusters(X, y_true, k_values=[2, 3, 4, 5])
    
    # 최적 K로 클러스터 분석
    print(f"\n📊 최적 K={optimal_k}로 클러스터 분석을 수행합니다...")
    plot_cluster_analysis(X, y_true, optimal_k)
    
    print("\n" + "=" * 60)
    print("🎉 K-means 클러스터링 시각화가 완료되었습니다!")
    print("📁 생성된 파일들:")
    print("   - kmeans_elbow_analysis.png (엘보우 분석)")
    print("   - kmeans_clusters_comparison.png (클러스터 비교)")
    print("   - kmeans_optimal_clusters.png (최적 클러스터)")
    print("=" * 60)

if __name__ == "__main__":
    main()
