#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
엘보우 기법 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.nlp import Nlp
import numpy as np

def test_elbow_method():
    """엘보우 기법 테스트"""
    print("🚀 엘보우 기법 테스트를 시작합니다...")
    
    # NLP 객체 생성
    nlp = Nlp()
    
    # 모델 로드
    nlp.LoadModel()
    
    if nlp.model is None:
        print("❌ Word2Vec 모델이 없습니다. 먼저 모델을 학습시켜주세요.")
        return
    
    print("✅ 모델이 성공적으로 로드되었습니다.")
    print(f"📊 모델 어휘 크기: {len(nlp.model.wv.key_to_index)}")
    
    # 테스트할 단어 수 설정
    test_word_count = 500
    word_list = list(nlp.model.wv.key_to_index)[:test_word_count]
    
    print(f"🔍 {test_word_count}개 단어로 엘보우 기법을 테스트합니다...")
    
    try:
        # 엘보우 기법을 사용한 클러스터링
        reduced_vectors, labels, cluster_groups = nlp.find_clusters_with_elbow(
            word_list=word_list,
            max_clusters=15,
            method='kmeans'
        )
        
        if reduced_vectors is not None:
            print("\n🎉 엘보우 기법 테스트가 성공적으로 완료되었습니다!")
            print(f"📊 생성된 클러스터 수: {len(cluster_groups)}")
            print(f"📊 총 단어 수: {len(word_list)}")
            
            # 각 클러스터의 상세 정보 출력
            print("\n📋 클러스터 상세 정보:")
            for cluster_id, words in cluster_groups.items():
                print(f"\n🔸 클러스터 {cluster_id} ({len(words)}개 단어):")
                if len(words) <= 15:
                    print(f"   단어들: {', '.join(words)}")
                else:
                    print(f"   대표 단어들: {', '.join(words[:10])}... (총 {len(words)}개)")
        else:
            print("❌ 클러스터링에 실패했습니다.")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()

def test_elbow_plot_only():
    """엘보우 그래프만 테스트"""
    print("📊 엘보우 그래프 테스트를 시작합니다...")
    
    # NLP 객체 생성
    nlp = Nlp()
    
    # 모델 로드
    nlp.LoadModel()
    
    if nlp.model is None:
        print("❌ Word2Vec 모델이 없습니다. 먼저 모델을 학습시켜주세요.")
        return
    
    # 테스트할 단어 수 설정
    test_word_count = 300
    word_list = list(nlp.model.wv.key_to_index)[:test_word_count]
    
    # 벡터 추출
    word_vectors = np.array([nlp.model.wv[word] for word in word_list])
    
    # 차원 축소
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    
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
    
    try:
        # 엘보우 그래프만 표시
        optimal_clusters, inertias, silhouette_scores, cluster_range = nlp.plot_elbow_method(
            reduced_vectors, 
            max_clusters=15,
            save_path="elbow_plot.png"
        )
        
        print(f"✅ 엘보우 그래프가 생성되었습니다!")
        print(f"📊 최적 클러스터 수: {optimal_clusters}")
        
    except Exception as e:
        print(f"❌ 엘보우 그래프 생성 중 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🔬 엘보우 기법 테스트 프로그램")
    print("=" * 60)
    
    # 사용자 선택
    print("\n테스트할 기능을 선택하세요:")
    print("1. 전체 엘보우 기법 테스트 (클러스터링 + 그래프)")
    print("2. 엘보우 그래프만 테스트")
    
    choice = input("\n선택 (1 또는 2): ").strip()
    
    if choice == "1":
        test_elbow_method()
    elif choice == "2":
        test_elbow_plot_only()
    else:
        print("❌ 잘못된 선택입니다. 1 또는 2를 입력해주세요.")
    
    print("\n" + "=" * 60)
    print("🏁 테스트가 완료되었습니다.")
    print("=" * 60)
