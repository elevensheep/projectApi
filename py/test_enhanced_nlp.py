#!/usr/bin/env python3
"""
향상된 NLP 시스템 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.nlp import Nlp
from app.services.database import MySQLDatabase
from app.utils.recommendation_runner import evaluate_recommendation_quality
import time

def test_enhanced_nlp():
    """향상된 NLP 시스템 테스트"""
    print("🚀 향상된 NLP 시스템 테스트 시작")
    print("=" * 50)
    
    # 1. 데이터베이스 설정
    print("📊 1. 데이터베이스 설정...")
    db = MySQLDatabase()
    db.add_similarity_score_column()
    db.update_similarity_scores()
    
    # 2. NLP 모델 초기화
    print("\n🤖 2. NLP 모델 초기화...")
    nlp = Nlp()
    
    # 3. 모델 학습 (기존 모델이 없으면)
    if not os.path.exists("word2vec.model"):
        print("📚 3. Word2Vec 모델 학습 중...")
        start_time = time.time()
        isbn_tokens = nlp.train_book_model_and_get_tokens()
        end_time = time.time()
        print(f"✅ 모델 학습 완료 (소요시간: {end_time - start_time:.2f}초)")
    else:
        print("📚 3. 기존 모델 로드 중...")
        nlp.LoadModel()
    
    # 4. 유사도 테스트
    print("\n🔍 4. 유사도 테스트...")
    test_words = [
        ("경제", "금융"),
        ("정치", "정부"),
        ("스포츠", "축구"),
        ("교육", "학습"),
        ("기술", "과학")
    ]
    
    for word1, word2 in test_words:
        print(f"\n테스트: '{word1}' ↔ '{word2}'")
        nlp.ModelScore(word1, word2)
    
    # 5. 유사 단어 테스트
    print("\n🔍 5. 유사 단어 테스트...")
    test_keywords = ["경제", "정치", "스포츠", "교육", "기술"]
    
    for keyword in test_keywords:
        print(f"\n'{keyword}'와 유사한 단어들:")
        similar_words = nlp.SimilerWord(keyword, topn=3)
        for word, score, model in similar_words:
            print(f"  - {word} (점수: {score:.4f}, 모델: {model})")
    
    # 6. 클러스터링 테스트
    print("\n📊 6. 클러스터링 테스트...")
    try:
        nlp.VisualizeModel(word_list=None, num_clusters=8, method='kmeans')
        print("✅ 클러스터링 시각화 완료")
    except Exception as e:
        print(f"⚠️ 클러스터링 시각화 실패: {e}")
    
    # 7. 추천 품질 평가
    print("\n📈 7. 추천 품질 평가...")
    evaluate_recommendation_quality()
    
    # 8. 성능 테스트
    print("\n⚡ 8. 성능 테스트...")
    test_descriptions = [
        "경제 위기와 금융 시장의 변화에 대한 분석",
        "정치 개혁과 민주주의 발전 방향",
        "스포츠 선수들의 경기력 향상 방법",
        "교육 혁신과 미래 인재 양성",
        "기술 발전과 과학 연구의 최신 동향"
    ]
    
    start_time = time.time()
    for desc in test_descriptions:
        tokens = nlp.extract_nouns_enhanced([desc])
        print(f"  '{desc}' → {tokens}")
    end_time = time.time()
    
    print(f"✅ 토큰 추출 성능: {len(test_descriptions)}개 문장 처리 시간 {end_time - start_time:.4f}초")
    
    db.close()
    print("\n🎉 향상된 NLP 시스템 테스트 완료!")

def test_recommendation_accuracy():
    """추천 정확도 테스트"""
    print("\n🎯 추천 정확도 테스트")
    print("=" * 30)
    
    from app.utils.recommendation_runner import (
        find_direct_matches, 
        find_similarity_matches, 
        find_cluster_matches,
        combine_matches
    )
    
    db = MySQLDatabase()
    nlp = Nlp()
    nlp.LoadModel()
    
    test_keywords = ["경제", "정치", "스포츠", "교육"]
    test_category = "economy"
    
    for keyword in test_keywords:
        print(f"\n🔍 키워드: '{keyword}'")
        
        # 직접 매칭
        direct_matches = find_direct_matches(db, keyword)
        print(f"  직접 매칭: {len(direct_matches)}개")
        
        # 유사도 매칭
        similarity_matches = find_similarity_matches(nlp, db, keyword)
        print(f"  유사도 매칭: {len(similarity_matches)}개")
        
        # 클러스터 매칭
        cluster_matches = find_cluster_matches(nlp, db, keyword, test_category)
        print(f"  클러스터 매칭: {len(cluster_matches)}개")
        
        # 통합 매칭
        combined_matches = combine_matches(direct_matches, similarity_matches, cluster_matches)
        print(f"  통합 매칭: {len(combined_matches)}개")
        
        if combined_matches:
            print(f"  최고 점수: {combined_matches[0][1]:.4f}")
    
    db.close()

if __name__ == "__main__":
    try:
        test_enhanced_nlp()
        test_recommendation_accuracy()
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc() 