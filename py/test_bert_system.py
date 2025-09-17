#!/usr/bin/env python3
"""
BERT 기반 향상된 NLP 시스템 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.bert_nlp import BertNLP
from app.services.database import MySQLDatabase
from app.utils.bert_recommendation import BertRecommendationSystem
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bert_nlp():
    """BERT NLP 시스템 테스트"""
    print("🚀 BERT NLP 시스템 테스트 시작")
    print("=" * 50)
    
    try:
        # BERT NLP 초기화
        print("🤖 BERT NLP 모델 초기화 중...")
        bert_nlp = BertNLP()
        print("✅ BERT NLP 모델 초기화 완료")
        
        # 1. 문맥 기반 유사도 테스트
        print("\n🔍 1. 문맥 기반 유사도 테스트...")
        test_pairs = [
            ("경제 위기", "금융 시장의 불안정성"),
            ("정치 개혁", "민주주의 발전"),
            ("스포츠 경기", "축구 선수들의 활약"),
            ("교육 혁신", "미래 인재 양성"),
            ("기술 발전", "과학 연구의 최신 동향")
        ]
        
        for text1, text2 in test_pairs:
            similarity = bert_nlp.calculate_contextual_similarity(text1, text2)
            print(f"  '{text1}' ↔ '{text2}': {similarity:.4f}")
        
        # 2. 감정 분석 테스트
        print("\n😊 2. 감정 분석 테스트...")
        test_texts = [
            "이 책은 정말 훌륭하고 감동적인 내용을 담고 있습니다.",
            "슬프고 비극적인 이야기로 가슴이 아픕니다.",
            "일반적인 경제 이론에 대한 설명입니다.",
            "희망적이고 밝은 미래를 그리는 내용입니다.",
            "화가 나고 실망스러운 상황을 다룹니다."
        ]
        
        for text in test_texts:
            sentiment = bert_nlp.analyze_sentiment(text)
            dominant = bert_nlp.get_dominant_sentiment(text)
            print(f"  '{text[:30]}...' → {dominant} (긍정: {sentiment['positive']:.3f}, 부정: {sentiment['negative']:.3f}, 중립: {sentiment['neutral']:.3f})")
        
        # 3. 유사 텍스트 검색 테스트
        print("\n🔍 3. 유사 텍스트 검색 테스트...")
        query = "경제 발전과 성장"
        candidates = [
            "경제 위기와 금융 시장의 변화",
            "정치 개혁과 민주주의 발전",
            "스포츠 선수들의 경기력 향상",
            "금융 정책과 경제 성장",
            "교육 혁신과 미래 인재 양성"
        ]
        
        similar_texts = bert_nlp.find_similar_texts(query, candidates, top_k=3)
        print(f"  쿼리: '{query}'")
        for idx, score in similar_texts:
            print(f"    - '{candidates[idx]}': {score:.4f}")
        
        # 4. 텍스트 클러스터링 테스트
        print("\n📊 4. 텍스트 클러스터링 테스트...")
        clustering_texts = [
            "경제 위기와 금융 시장의 변화에 대한 분석",
            "정치 개혁과 민주주의 발전 방향",
            "스포츠 선수들의 경기력 향상 방법",
            "교육 혁신과 미래 인재 양성",
            "기술 발전과 과학 연구의 최신 동향",
            "금융 정책과 경제 성장 전략",
            "정치 스캔들과 부패 문제",
            "축구 경기와 선수들의 활약",
            "대학 교육과 학생들의 학습",
            "인공지능과 미래 기술"
        ]
        
        clusters = bert_nlp.cluster_texts(clustering_texts, n_clusters=3)
        print(f"  클러스터링 결과: {len(clusters)}개 클러스터")
        for cluster_id, text_indices in clusters.items():
            print(f"    클러스터 {cluster_id}: {len(text_indices)}개 텍스트")
            for idx in text_indices[:3]:  # 상위 3개만 출력
                print(f"      - {clustering_texts[idx][:30]}...")
        
        # 5. 임베딩 시각화 테스트
        print("\n📈 5. 임베딩 시각화 테스트...")
        try:
            bert_nlp.visualize_embeddings(
                clustering_texts[:8],  # 8개만 사용
                title="BERT 임베딩 시각화 테스트"
            )
            print("✅ 임베딩 시각화 완료")
        except Exception as e:
            print(f"⚠️ 임베딩 시각화 실패: {e}")
        
        # 6. 성능 테스트
        print("\n⚡ 6. 성능 테스트...")
        start_time = time.time()
        embeddings = bert_nlp.batch_process(clustering_texts, batch_size=4)
        end_time = time.time()
        
        print(f"✅ 배치 처리 성능: {len(clustering_texts)}개 텍스트 처리 시간 {end_time - start_time:.4f}초")
        print(f"   평균 처리 시간: {(end_time - start_time) / len(clustering_texts):.4f}초/텍스트")
        
        print("\n🎉 BERT NLP 시스템 테스트 완료!")
        
    except Exception as e:
        print(f"❌ BERT NLP 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

def test_bert_recommendation():
    """BERT 추천 시스템 테스트"""
    print("\n🎯 BERT 추천 시스템 테스트")
    print("=" * 40)
    
    try:
        # 데이터베이스 설정
        print("📊 데이터베이스 설정...")
        db = MySQLDatabase()
        db.add_similarity_score_column()
        db.add_method_column()
        db.update_similarity_scores()
        db.update_method_values()
        
        # BERT 추천 시스템 초기화
        print("🤖 BERT 추천 시스템 초기화...")
        bert_rec = BertRecommendationSystem()
        
        # 테스트용 뉴스 데이터
        test_news_data = {
            'economy': ['경제', '금융', '투자', '주식'],
            'politics': ['정치', '정부', '국회', '대통령'],
            'sports': ['스포츠', '축구', '야구', '선수']
        }
        
        # 1. 문맥 기반 추천 테스트
        print("\n🔍 1. 문맥 기반 추천 테스트...")
        context_recs = bert_rec.recommend_books_by_context(test_news_data)
        for category, recs in context_recs.items():
            print(f"  {category}: {len(recs)}개 추천")
            for isbn, score in recs[:3]:  # 상위 3개만 출력
                print(f"    - {isbn}: {score:.4f}")
        
        # 2. 감정 기반 추천 테스트
        print("\n😊 2. 감정 기반 추천 테스트...")
        sentiment_recs = bert_rec.recommend_books_by_sentiment(test_news_data)
        for keyword, recs in sentiment_recs.items():
            print(f"  {keyword}: {len(recs)}개 추천")
            for isbn, score in recs[:3]:  # 상위 3개만 출력
                print(f"    - {isbn}: {score:.4f}")
        
        # 3. 클러스터링 기반 추천 테스트
        print("\n📊 3. 클러스터링 기반 추천 테스트...")
        cluster_recs = bert_rec.recommend_books_by_clustering(test_news_data, n_clusters=3)
        for category, recs in cluster_recs.items():
            print(f"  {category}: {len(recs)}개 추천")
            for isbn, score in recs[:3]:  # 상위 3개만 출력
                print(f"    - {isbn}: {score:.4f}")
        
        # 4. 하이브리드 추천 테스트
        print("\n🚀 4. 하이브리드 추천 테스트...")
        hybrid_recs = bert_rec.hybrid_recommendation(test_news_data)
        for category, recs in hybrid_recs.items():
            print(f"  {category}: {len(recs)}개 추천")
            for isbn, score in recs[:3]:  # 상위 3개만 출력
                print(f"    - {isbn}: {score:.4f}")
        
        # 5. DB 저장 테스트
        print("\n💾 5. DB 저장 테스트...")
        bert_rec.save_recommendations_to_db(hybrid_recs, "hybrid")
        
        # 6. 품질 평가
        print("\n📈 6. 품질 평가...")
        bert_rec.evaluate_recommendation_quality("hybrid")
        
        bert_rec.close()
        db.close()
        
        print("\n🎉 BERT 추천 시스템 테스트 완료!")
        
    except Exception as e:
        print(f"❌ BERT 추천 시스템 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

def compare_methods():
    """기존 방법과 BERT 방법 비교"""
    print("\n⚖️ 기존 방법 vs BERT 방법 비교")
    print("=" * 40)
    
    try:
        from app.services.nlp import Nlp
        from app.utils.recommendation_runner import recommend_books_by_keywords_enhanced
        
        # 테스트용 뉴스 데이터
        test_news_data = {
            'economy': ['경제', '금융'],
            'politics': ['정치', '정부']
        }
        
        # 1. 기존 Word2Vec 방법
        print("📊 1. 기존 Word2Vec 방법...")
        start_time = time.time()
        
        nlp = Nlp()
        nlp.LoadModel()
        
        # 간단한 유사도 테스트
        test_words = [("경제", "금융"), ("정치", "정부")]
        for word1, word2 in test_words:
            nlp.ModelScore(word1, word2)
        
        w2v_time = time.time() - start_time
        print(f"   Word2Vec 처리 시간: {w2v_time:.4f}초")
        
        # 2. BERT 방법
        print("🤖 2. BERT 방법...")
        start_time = time.time()
        
        bert_nlp = BertNLP()
        
        # 문맥 기반 유사도 테스트
        test_texts = [("경제 발전", "금융 시장"), ("정치 개혁", "정부 정책")]
        for text1, text2 in test_texts:
            similarity = bert_nlp.calculate_contextual_similarity(text1, text2)
            print(f"   '{text1}' ↔ '{text2}': {similarity:.4f}")
        
        bert_time = time.time() - start_time
        print(f"   BERT 처리 시간: {bert_time:.4f}초")
        
        # 3. 성능 비교
        print("\n📈 3. 성능 비교 결과:")
        print(f"   Word2Vec: {w2v_time:.4f}초")
        print(f"   BERT: {bert_time:.4f}초")
        print(f"   성능 비율: {bert_time/w2v_time:.2f}배 (BERT가 더 느림)")
        print("   💡 BERT는 더 정확하지만 처리 시간이 더 오래 걸립니다.")
        
        print("\n🎉 방법 비교 완료!")
        
    except Exception as e:
        print(f"❌ 방법 비교 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        test_bert_nlp()
        test_bert_recommendation()
        compare_methods()
        
        print("\n" + "="*60)
        print("🎉 모든 BERT 시스템 테스트 완료!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ 전체 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc() 