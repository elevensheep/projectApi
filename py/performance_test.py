#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BERT 성능 비교 테스트
- 기존 BERT vs 최적화된 BERT
- 처리 시간 및 메모리 사용량 비교
"""

import sys
import os
import time
import psutil
import gc

# app 폴더를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
sys.path.append(app_dir)

from services.bert_nlp import BertNLP
from services.bert_nlp_optimized import OptimizedBertNLP
from services.crowling import Crowling
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_memory_usage():
    """현재 메모리 사용량 반환"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

def test_original_bert():
    """기존 BERT 성능 테스트"""
    logger.info("🧪 기존 BERT 성능 테스트 시작")
    
    # 메모리 사용량 초기
    initial_memory = get_memory_usage()
    
    # 기존 BERT 초기화
    start_time = time.time()
    bert_nlp = BertNLP()
    init_time = time.time() - start_time
    
    # 메모리 사용량 (초기화 후)
    init_memory = get_memory_usage()
    
    # 테스트 데이터
    test_texts = [
        "경제 위기와 금융 정책에 대한 분석",
        "정치 개혁과 민주주의 발전",
        "스포츠 경기 결과와 선수들의 활약",
        "사회 문제와 해결 방안",
        "국제 관계와 외교 정책"
    ] * 10  # 50개 텍스트
    
    # 임베딩 생성 테스트
    start_time = time.time()
    embeddings = []
    for text in test_texts:
        embedding = bert_nlp.get_bert_embedding(text)
        embeddings.append(embedding)
    embedding_time = time.time() - start_time
    
    # 메모리 사용량 (처리 후)
    final_memory = get_memory_usage()
    
    # 유사도 계산 테스트
    query = "경제와 금융에 관한 내용"
    start_time = time.time()
    
    similarities = []
    for text in test_texts:
        similarity = bert_nlp.calculate_contextual_similarity(query, text)
        similarities.append(similarity)
    
    similarity_time = time.time() - start_time
    
    # 결과 정리
    results = {
        'init_time': init_time,
        'embedding_time': embedding_time,
        'similarity_time': similarity_time,
        'total_time': init_time + embedding_time + similarity_time,
        'initial_memory': initial_memory,
        'init_memory': init_memory,
        'final_memory': final_memory,
        'memory_increase': final_memory - initial_memory,
        'texts_processed': len(test_texts),
        'processing_speed': len(test_texts) / embedding_time
    }
    
    logger.info(f"📊 기존 BERT 결과:")
    logger.info(f"   - 초기화 시간: {init_time:.2f}초")
    logger.info(f"   - 임베딩 생성 시간: {embedding_time:.2f}초")
    logger.info(f"   - 유사도 계산 시간: {similarity_time:.2f}초")
    logger.info(f"   - 총 처리 시간: {results['total_time']:.2f}초")
    logger.info(f"   - 처리 속도: {results['processing_speed']:.2f} 텍스트/초")
    logger.info(f"   - 메모리 증가: {results['memory_increase']:.2f}MB")
    
    # 메모리 정리
    del bert_nlp
    gc.collect()
    
    return results

def test_optimized_bert():
    """최적화된 BERT 성능 테스트"""
    logger.info("🚀 최적화된 BERT 성능 테스트 시작")
    
    # 메모리 사용량 초기
    initial_memory = get_memory_usage()
    
    # 최적화된 BERT 초기화
    start_time = time.time()
    bert_nlp = OptimizedBertNLP()
    init_time = time.time() - start_time
    
    # 메모리 사용량 (초기화 후)
    init_memory = get_memory_usage()
    
    # 테스트 데이터
    test_texts = [
        "경제 위기와 금융 정책에 대한 분석",
        "정치 개혁과 민주주의 발전",
        "스포츠 경기 결과와 선수들의 활약",
        "사회 문제와 해결 방안",
        "국제 관계와 외교 정책"
    ] * 10  # 50개 텍스트
    
    # 배치 임베딩 생성 테스트
    start_time = time.time()
    embeddings = bert_nlp.get_embeddings_batch(test_texts, batch_size=32)
    embedding_time = time.time() - start_time
    
    # 메모리 사용량 (처리 후)
    final_memory = get_memory_usage()
    
    # 배치 유사도 계산 테스트
    query = "경제와 금융에 관한 내용"
    start_time = time.time()
    
    similarities = bert_nlp.calculate_similarities_batch(query, test_texts)
    
    similarity_time = time.time() - start_time
    
    # 캐시 저장
    bert_nlp.save_cache()
    
    # 결과 정리
    results = {
        'init_time': init_time,
        'embedding_time': embedding_time,
        'similarity_time': similarity_time,
        'total_time': init_time + embedding_time + similarity_time,
        'initial_memory': initial_memory,
        'init_memory': init_memory,
        'final_memory': final_memory,
        'memory_increase': final_memory - initial_memory,
        'texts_processed': len(test_texts),
        'processing_speed': len(test_texts) / embedding_time,
        'cache_stats': bert_nlp.get_cache_stats()
    }
    
    logger.info(f"📊 최적화된 BERT 결과:")
    logger.info(f"   - 초기화 시간: {init_time:.2f}초")
    logger.info(f"   - 임베딩 생성 시간: {embedding_time:.2f}초")
    logger.info(f"   - 유사도 계산 시간: {similarity_time:.2f}초")
    logger.info(f"   - 총 처리 시간: {results['total_time']:.2f}초")
    logger.info(f"   - 처리 속도: {results['processing_speed']:.2f} 텍스트/초")
    logger.info(f"   - 메모리 증가: {results['memory_increase']:.2f}MB")
    logger.info(f"   - 캐시 통계: {results['cache_stats']}")
    
    # 메모리 정리
    del bert_nlp
    gc.collect()
    
    return results

def compare_performance():
    """성능 비교"""
    logger.info("⚖️ BERT 성능 비교 시작")
    
    # 기존 BERT 테스트
    original_results = test_original_bert()
    
    # 잠시 대기 (메모리 정리)
    time.sleep(2)
    gc.collect()
    
    # 최적화된 BERT 테스트
    optimized_results = test_optimized_bert()
    
    # 성능 비교
    logger.info("\n" + "="*60)
    logger.info("📈 성능 비교 결과")
    logger.info("="*60)
    
    # 처리 시간 비교
    time_improvement = (original_results['total_time'] - optimized_results['total_time']) / original_results['total_time'] * 100
    logger.info(f"⏱️ 처리 시간:")
    logger.info(f"   - 기존 BERT: {original_results['total_time']:.2f}초")
    logger.info(f"   - 최적화된 BERT: {optimized_results['total_time']:.2f}초")
    logger.info(f"   - 개선율: {time_improvement:.1f}%")
    
    # 처리 속도 비교
    speed_improvement = (optimized_results['processing_speed'] - original_results['processing_speed']) / original_results['processing_speed'] * 100
    logger.info(f"🚀 처리 속도:")
    logger.info(f"   - 기존 BERT: {original_results['processing_speed']:.2f} 텍스트/초")
    logger.info(f"   - 최적화된 BERT: {optimized_results['processing_speed']:.2f} 텍스트/초")
    logger.info(f"   - 개선율: {speed_improvement:.1f}%")
    
    # 메모리 사용량 비교
    memory_improvement = (original_results['memory_increase'] - optimized_results['memory_increase']) / original_results['memory_increase'] * 100
    logger.info(f"💾 메모리 사용량:")
    logger.info(f"   - 기존 BERT: {original_results['memory_increase']:.2f}MB 증가")
    logger.info(f"   - 최적화된 BERT: {optimized_results['memory_increase']:.2f}MB 증가")
    logger.info(f"   - 개선율: {memory_improvement:.1f}%")
    
    # 초기화 시간 비교
    init_improvement = (original_results['init_time'] - optimized_results['init_time']) / original_results['init_time'] * 100
    logger.info(f"🔧 초기화 시간:")
    logger.info(f"   - 기존 BERT: {original_results['init_time']:.2f}초")
    logger.info(f"   - 최적화된 BERT: {optimized_results['init_time']:.2f}초")
    logger.info(f"   - 개선율: {init_improvement:.1f}%")
    
    logger.info("\n" + "="*60)
    logger.info("🎯 최적화 효과 요약:")
    logger.info(f"   - 처리 시간 단축: {time_improvement:.1f}%")
    logger.info(f"   - 처리 속도 향상: {speed_improvement:.1f}%")
    logger.info(f"   - 메모리 효율성: {memory_improvement:.1f}%")
    logger.info(f"   - 초기화 속도: {init_improvement:.1f}%")
    logger.info("="*60)

def test_real_world_scenario():
    """실제 사용 시나리오 테스트"""
    logger.info("🌍 실제 사용 시나리오 테스트 시작")
    
    try:
        # 크롤러로 실제 뉴스 데이터 가져오기
        crawler = Crowling()
        news_data = crawler.wordExtraction()
        
        logger.info(f"📰 크롤링된 뉴스 데이터: {news_data}")
        
        # 최적화된 BERT로 실제 추천 테스트
        from utils.bert_recommendation_optimized import OptimizedBertRecommendationSystem
        
        start_time = time.time()
        
        recommender = OptimizedBertRecommendationSystem(
            batch_size=64,
            max_workers=4
        )
        
        # 캐시 로드
        recommender.load_cache()
        
        # 추천 실행
        recommendations = recommender.recommend_books_by_context_optimized(news_data)
        
        total_time = time.time() - start_time
        
        logger.info(f"⏱️ 실제 추천 처리 시간: {total_time:.2f}초")
        logger.info(f"📊 추천 결과:")
        
        total_recommendations = 0
        for category, recs in recommendations.items():
            logger.info(f"   - {category}: {len(recs)}권")
            total_recommendations += len(recs)
        
        logger.info(f"   총 추천 수: {total_recommendations}권")
        
        # 캐시 저장
        recommender.save_cache()
        recommender.close()
        
    except Exception as e:
        logger.error(f"❌ 실제 시나리오 테스트 실패: {e}")

if __name__ == "__main__":
    # 성능 비교 테스트
    compare_performance()
    
    # 실제 시나리오 테스트
    test_real_world_scenario()
