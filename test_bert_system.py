#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BERT 기반 NLP 및 추천 시스템 테스트
- 문맥 기반 유사도 매칭
- 키워드 기반 추천
- 클러스터링 기반 추천
"""

import sys
import os
import logging
from typing import List, Dict

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from py.app.services.bert_nlp import BertNLP
from py.app.utils.bert_recommendation import BertRecommendationSystem
from py.app.services.database import MySQLDatabase

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_bert_nlp():
    """BERT NLP 기능 테스트"""
    logger.info("🧪 BERT NLP 기능 테스트 시작")
    
    try:
        # BERT NLP 초기화
        bert_nlp = BertNLP()
        
        # 테스트 텍스트들
        test_texts = [
            "경제 위기와 투자 전략",
            "주식 시장 분석과 투자 방법",
            "사회 문제와 해결책",
            "정치 현안과 민주주의",
            "스포츠 경기 결과와 선수 분석"
        ]
        
        # 1. 문맥 기반 유사도 계산 테스트
        logger.info("📊 문맥 기반 유사도 계산 테스트")
        text1 = "경제 위기와 투자 전략"
        text2 = "주식 시장 분석과 투자 방법"
        similarity = bert_nlp.calculate_contextual_similarity(text1, text2)
        logger.info(f"  '{text1}' vs '{text2}': {similarity:.4f}")
        
        # 2. 유사 텍스트 검색 테스트
        logger.info("🔍 유사 텍스트 검색 테스트")
        query = "경제 투자"
        similar_texts = bert_nlp.find_similar_texts(query, test_texts, top_k=3)
        logger.info(f"  쿼리: '{query}'")
        for idx, score in similar_texts:
            logger.info(f"    - {test_texts[idx]}: {score:.4f}")
        
        # 3. 키워드 추출 테스트
        logger.info("🔑 키워드 추출 테스트")
        sample_text = "경제 위기 상황에서 투자자들이 취해야 할 전략과 주식 시장 분석 방법"
        keywords = bert_nlp.extract_keywords(sample_text, top_k=5)
        logger.info(f"  텍스트: '{sample_text}'")
        logger.info(f"  키워드: {keywords}")
        
        # 4. 단어 유사도 계산 테스트
        logger.info("📈 단어 유사도 계산 테스트")
        word_pairs = [
            ("경제", "투자"),
            ("주식", "시장"),
            ("사회", "문제"),
            ("정치", "민주주의")
        ]
        for word1, word2 in word_pairs:
            similarity = bert_nlp.calculate_word_similarity(word1, word2)
            logger.info(f"  '{word1}' vs '{word2}': {similarity:.4f}")
        
        # 5. 텍스트 클러스터링 테스트
        logger.info("📊 텍스트 클러스터링 테스트")
        clusters = bert_nlp.cluster_texts(test_texts, n_clusters=3)
        for cluster_id, text_indices in clusters.items():
            logger.info(f"  클러스터 {cluster_id}:")
            for idx in text_indices:
                logger.info(f"    - {test_texts[idx]}")
        
        # 6. 임베딩 시각화 테스트 (옵션)
        logger.info("📈 임베딩 시각화 테스트")
        try:
            bert_nlp.visualize_embeddings(test_texts, title="테스트 텍스트 임베딩")
            logger.info("  ✅ 시각화 완료")
        except Exception as e:
            logger.warning(f"  ⚠️ 시각화 실패: {e}")
        
        # 7. 배치 처리 테스트
        logger.info("⚡ 배치 처리 테스트")
        embeddings = bert_nlp.batch_process(test_texts, batch_size=2)
        logger.info(f"  배치 처리된 임베딩 수: {len(embeddings)}")
        
        # 8. 텍스트 특성 추출 테스트
        logger.info("🔧 텍스트 특성 추출 테스트")
        features = bert_nlp.get_text_features(sample_text)
        logger.info(f"  텍스트 길이: {features['length']}")
        logger.info(f"  단어 수: {features['word_count']}")
        logger.info(f"  키워드: {features['keywords']}")
        
        logger.info("✅ BERT NLP 기능 테스트 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ BERT NLP 테스트 실패: {e}")
        return False

def test_bert_recommendation():
    """BERT 추천 시스템 테스트"""
    logger.info("🧪 BERT 추천 시스템 테스트 시작")
    
    try:
        # 추천 시스템 초기화
        recommender = BertRecommendationSystem()
        
        # 실제 뉴스 제목으로 테스트
        from py.app.services.crowling import Crowling
        crawler = Crowling()
        
        logger.info("📡 실제 뉴스 제목 크롤링 중...")
        news_titles = crawler.get_news_titles()
        
        if not news_titles:
            logger.warning("⚠️ 뉴스 제목을 가져올 수 없어 테스트 데이터 사용")
            # 테스트용 뉴스 데이터
            news_titles = {
                "경제": ["주식 투자", "경제 위기", "투자 전략"],
                "사회": ["사회 문제", "해결책", "개선 방안"],
                "정치": ["정치 현안", "민주주의", "정책"]
            }
        
        logger.info(f"📰 테스트용 뉴스 제목: {len(news_titles)}개 카테고리")
        
        # 1. 문맥 기반 추천 테스트
        logger.info("🧠 문맥 기반 추천 테스트")
        context_recs = recommender.recommend_books_by_context(news_titles)
        for category, recs in context_recs.items():
            logger.info(f"  {category}: {len(recs)}개 추천")
            for isbn, score in recs[:3]:  # 상위 3개만 출력
                logger.info(f"    - {isbn}: {score:.4f}")
        
        # 2. 키워드 기반 추천 테스트
        logger.info("🔍 키워드 기반 추천 테스트")
        keyword_recs = recommender.recommend_books_by_keywords(news_titles)
        for keyword, recs in keyword_recs.items():
            logger.info(f"  {keyword}: {len(recs)}개 추천")
            for isbn, score in recs[:3]:
                logger.info(f"    - {isbn}: {score:.4f}")
        
        # 3. 클러스터링 기반 추천 테스트
        logger.info("📊 클러스터링 기반 추천 테스트")
        cluster_recs = recommender.recommend_books_by_clustering(news_titles, n_clusters=3)
        for keyword, recs in cluster_recs.items():
            logger.info(f"  {keyword}: {len(recs)}개 추천")
            for isbn, score in recs[:3]:
                logger.info(f"    - {isbn}: {score:.4f}")
        
        # 4. 하이브리드 추천 테스트
        logger.info("🔄 하이브리드 추천 테스트")
        hybrid_recs = recommender.hybrid_recommendation(news_titles)
        for keyword, recs in hybrid_recs.items():
            logger.info(f"  {keyword}: {len(recs)}개 추천")
            for isbn, score in recs[:3]:
                logger.info(f"    - {isbn}: {score:.4f}")
        
        # 5. DB 저장 테스트 (옵션)
        logger.info("💾 DB 저장 테스트")
        try:
            recommender.save_recommendations_to_db(hybrid_recs, "test_hybrid")
            logger.info("  ✅ DB 저장 완료")
        except Exception as e:
            logger.warning(f"  ⚠️ DB 저장 실패: {e}")
        
        # 6. 품질 평가 테스트
        logger.info("📈 품질 평가 테스트")
        try:
            recommender.evaluate_recommendation_quality("test_hybrid")
        except Exception as e:
            logger.warning(f"  ⚠️ 품질 평가 실패: {e}")
        
        # 리소스 정리
        recommender.close()
        
        logger.info("✅ BERT 추천 시스템 테스트 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ BERT 추천 시스템 테스트 실패: {e}")
        return False

def compare_methods():
    """전통적 방법과 BERT 방법 비교"""
    logger.info("🔄 전통적 방법과 BERT 방법 비교")
    
    try:
        # 테스트 데이터
        test_texts = [
            "경제 위기와 투자 전략",
            "주식 시장 분석과 투자 방법",
            "사회 문제와 해결책"
        ]
        
        # BERT NLP 초기화
        bert_nlp = BertNLP()
        
        # 1. 유사도 계산 비교
        logger.info("📊 유사도 계산 비교")
        text1 = "경제 투자"
        text2 = "주식 시장"
        
        # BERT 기반 유사도
        bert_similarity = bert_nlp.calculate_contextual_similarity(text1, text2)
        logger.info(f"  BERT 유사도: {bert_similarity:.4f}")
        
        # 2. 키워드 추출 비교
        logger.info("🔑 키워드 추출 비교")
        sample_text = "경제 위기 상황에서 투자자들이 취해야 할 전략"
        
        # BERT 기반 키워드
        bert_keywords = bert_nlp.extract_keywords(sample_text, top_k=5)
        logger.info(f"  BERT 키워드: {bert_keywords}")
        
        # 3. 성능 비교
        logger.info("⚡ 성능 비교")
        import time
        
        # BERT 처리 시간 측정
        start_time = time.time()
        for _ in range(10):
            bert_nlp.calculate_contextual_similarity(text1, text2)
        bert_time = time.time() - start_time
        
        logger.info(f"  BERT 10회 처리 시간: {bert_time:.4f}초")
        
        logger.info("✅ 방법 비교 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ 방법 비교 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    logger.info("🚀 BERT 시스템 종합 테스트 시작")
    
    # 테스트 실행
    tests = [
        ("BERT NLP 기능", test_bert_nlp),
        ("BERT 추천 시스템", test_bert_recommendation),
        ("방법 비교", compare_methods)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 {test_name} 테스트")
        logger.info(f"{'='*50}")
        
        try:
            success = test_func()
            results[test_name] = "✅ 성공" if success else "❌ 실패"
        except Exception as e:
            logger.error(f"❌ {test_name} 테스트 예외 발생: {e}")
            results[test_name] = "❌ 예외"
    
    # 결과 요약
    logger.info(f"\n{'='*50}")
    logger.info("📊 테스트 결과 요약")
    logger.info(f"{'='*50}")
    
    for test_name, result in results.items():
        logger.info(f"  {test_name}: {result}")
    
    success_count = sum(1 for result in results.values() if "성공" in result)
    total_count = len(results)
    
    logger.info(f"\n  전체 성공률: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        logger.info("🎉 모든 테스트 통과!")
    else:
        logger.warning("⚠️ 일부 테스트 실패")
    
    logger.info("🏁 BERT 시스템 테스트 완료")

if __name__ == "__main__":
    main() 