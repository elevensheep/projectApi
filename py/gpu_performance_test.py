#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPU 성능 테스트
- GPU vs CPU 성능 비교
- GPU 메모리 사용량 모니터링
- 배치 크기별 성능 측정
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
from services.bert_nlp_gpu_optimized import GPUBertNLP
from services.crowling import Crowling
import logging
import torch

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_memory_usage():
    """현재 메모리 사용량 반환"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

def test_cpu_bert():
    """CPU BERT 성능 테스트"""
    logger.info("🧪 CPU BERT 성능 테스트 시작")
    
    # 메모리 사용량 초기
    initial_memory = get_memory_usage()
    
    # CPU BERT 초기화
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
    ] * 20  # 100개 텍스트
    
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
    
    logger.info(f"📊 CPU BERT 결과:")
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

def test_gpu_bert():
    """GPU BERT 성능 테스트"""
    logger.info("🚀 GPU BERT 성능 테스트 시작")
    
    # GPU 사용 가능 여부 확인
    if not torch.cuda.is_available():
        logger.warning("⚠️ GPU를 사용할 수 없습니다. CPU 테스트로 대체합니다.")
        return test_cpu_bert()
    
    # 메모리 사용량 초기
    initial_memory = get_memory_usage()
    
    # GPU BERT 초기화
    start_time = time.time()
    bert_nlp = GPUBertNLP()
    init_time = time.time() - start_time
    
    # 메모리 사용량 (초기화 후)
    init_memory = get_memory_usage()
    
    # GPU 통계 출력
    gpu_stats = bert_nlp.get_gpu_stats()
    logger.info(f"🎮 GPU 통계: {gpu_stats}")
    
    # 테스트 데이터
    test_texts = [
        "경제 위기와 금융 정책에 대한 분석",
        "정치 개혁과 민주주의 발전",
        "스포츠 경기 결과와 선수들의 활약",
        "사회 문제와 해결 방안",
        "국제 관계와 외교 정책"
    ] * 20  # 100개 텍스트
    
    # GPU 배치 임베딩 생성 테스트
    start_time = time.time()
    embeddings = bert_nlp.get_embeddings_batch_gpu(test_texts, batch_size=32)
    embedding_time = time.time() - start_time
    
    # 메모리 사용량 (처리 후)
    final_memory = get_memory_usage()
    
    # GPU 배치 유사도 계산 테스트
    query = "경제와 금융에 관한 내용"
    start_time = time.time()
    
    similarities = bert_nlp.calculate_similarities_batch_gpu(query, test_texts)
    
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
        'gpu_stats': gpu_stats
    }
    
    logger.info(f"📊 GPU BERT 결과:")
    logger.info(f"   - 초기화 시간: {init_time:.2f}초")
    logger.info(f"   - 임베딩 생성 시간: {embedding_time:.2f}초")
    logger.info(f"   - 유사도 계산 시간: {similarity_time:.2f}초")
    logger.info(f"   - 총 처리 시간: {results['total_time']:.2f}초")
    logger.info(f"   - 처리 속도: {results['processing_speed']:.2f} 텍스트/초")
    logger.info(f"   - 메모리 증가: {results['memory_increase']:.2f}MB")
    logger.info(f"   - GPU 메모리 사용률: {gpu_stats['memory_usage_percent']:.1f}%")
    
    # 메모리 정리
    del bert_nlp
    gc.collect()
    
    return results

def test_batch_size_performance():
    """배치 크기별 성능 테스트"""
    logger.info("📦 배치 크기별 성능 테스트 시작")
    
    if not torch.cuda.is_available():
        logger.warning("⚠️ GPU를 사용할 수 없습니다. CPU 테스트로 대체합니다.")
        return
    
    # 테스트 데이터
    test_texts = [
        "경제 위기와 금융 정책에 대한 분석",
        "정치 개혁과 민주주의 발전",
        "스포츠 경기 결과와 선수들의 활약",
        "사회 문제와 해결 방안",
        "국제 관계와 외교 정책"
    ] * 40  # 200개 텍스트
    
    # 배치 크기별 테스트
    batch_sizes = [8, 16, 32, 64, 128]
    
    results = {}
    
    for batch_size in batch_sizes:
        logger.info(f"🔍 배치 크기 {batch_size} 테스트 중...")
        
        # GPU BERT 초기화
        bert_nlp = GPUBertNLP()
        
        # GPU 메모리 초기화
        bert_nlp.clear_gpu_cache()
        
        # 배치 처리 테스트
        start_time = time.time()
        embeddings = bert_nlp.get_embeddings_batch_gpu(test_texts, batch_size=batch_size)
        end_time = time.time()
        
        # GPU 통계
        gpu_stats = bert_nlp.get_gpu_stats()
        
        # 결과 저장
        results[batch_size] = {
            'time': end_time - start_time,
            'speed': len(test_texts) / (end_time - start_time),
            'memory_usage': gpu_stats['memory_usage_percent']
        }
        
        logger.info(f"   - 처리 시간: {results[batch_size]['time']:.2f}초")
        logger.info(f"   - 처리 속도: {results[batch_size]['speed']:.2f} 텍스트/초")
        logger.info(f"   - GPU 메모리 사용률: {results[batch_size]['memory_usage']:.1f}%")
        
        # 메모리 정리
        del bert_nlp
        gc.collect()
    
    # 최적 배치 크기 찾기
    best_batch_size = max(results.keys(), key=lambda x: results[x]['speed'])
    logger.info(f"🏆 최적 배치 크기: {best_batch_size}")
    logger.info(f"   - 최고 처리 속도: {results[best_batch_size]['speed']:.2f} 텍스트/초")
    
    return results

def compare_gpu_cpu_performance():
    """GPU vs CPU 성능 비교"""
    logger.info("⚖️ GPU vs CPU 성능 비교 시작")
    
    # CPU BERT 테스트
    cpu_results = test_cpu_bert()
    
    # 잠시 대기 (메모리 정리)
    time.sleep(2)
    gc.collect()
    
    # GPU BERT 테스트
    gpu_results = test_gpu_bert()
    
    # 성능 비교
    logger.info("\n" + "="*60)
    logger.info("📈 GPU vs CPU 성능 비교 결과")
    logger.info("="*60)
    
    # 처리 시간 비교
    time_improvement = (cpu_results['total_time'] - gpu_results['total_time']) / cpu_results['total_time'] * 100
    logger.info(f"⏱️ 처리 시간:")
    logger.info(f"   - CPU BERT: {cpu_results['total_time']:.2f}초")
    logger.info(f"   - GPU BERT: {gpu_results['total_time']:.2f}초")
    logger.info(f"   - 개선율: {time_improvement:.1f}%")
    
    # 처리 속도 비교
    speed_improvement = (gpu_results['processing_speed'] - cpu_results['processing_speed']) / cpu_results['processing_speed'] * 100
    logger.info(f"🚀 처리 속도:")
    logger.info(f"   - CPU BERT: {cpu_results['processing_speed']:.2f} 텍스트/초")
    logger.info(f"   - GPU BERT: {gpu_results['processing_speed']:.2f} 텍스트/초")
    logger.info(f"   - 개선율: {speed_improvement:.1f}%")
    
    # 메모리 사용량 비교
    memory_improvement = (cpu_results['memory_increase'] - gpu_results['memory_increase']) / cpu_results['memory_increase'] * 100
    logger.info(f"💾 메모리 사용량:")
    logger.info(f"   - CPU BERT: {cpu_results['memory_increase']:.2f}MB 증가")
    logger.info(f"   - GPU BERT: {gpu_results['memory_increase']:.2f}MB 증가")
    logger.info(f"   - 개선율: {memory_improvement:.1f}%")
    
    # 초기화 시간 비교
    init_improvement = (cpu_results['init_time'] - gpu_results['init_time']) / cpu_results['init_time'] * 100
    logger.info(f"🔧 초기화 시간:")
    logger.info(f"   - CPU BERT: {cpu_results['init_time']:.2f}초")
    logger.info(f"   - GPU BERT: {gpu_results['init_time']:.2f}초")
    logger.info(f"   - 개선율: {init_improvement:.1f}%")
    
    logger.info("\n" + "="*60)
    logger.info("🎯 GPU 최적화 효과 요약:")
    logger.info(f"   - 처리 시간 단축: {time_improvement:.1f}%")
    logger.info(f"   - 처리 속도 향상: {speed_improvement:.1f}%")
    logger.info(f"   - 메모리 효율성: {memory_improvement:.1f}%")
    logger.info(f"   - 초기화 속도: {init_improvement:.1f}%")
    logger.info("="*60)

def test_real_world_gpu_scenario():
    """실제 GPU 사용 시나리오 테스트"""
    logger.info("🌍 실제 GPU 사용 시나리오 테스트 시작")
    
    try:
        # 크롤러로 실제 뉴스 데이터 가져오기
        crawler = Crowling()
        news_data = crawler.wordExtraction()
        
        logger.info(f"📰 크롤링된 뉴스 데이터: {news_data}")
        
        # GPU 최적화된 BERT로 실제 추천 테스트
        from utils.bert_recommendation_gpu import GPUBertRecommendationSystem
        
        start_time = time.time()
        
        recommender = GPUBertRecommendationSystem(
            batch_size=128,
            max_workers=2
        )
        
        # 캐시 로드
        recommender.load_cache()
        
        # 추천 실행
        recommendations = recommender.recommend_books_by_context_gpu(news_data)
        
        total_time = time.time() - start_time
        
        logger.info(f"⏱️ 실제 GPU 추천 처리 시간: {total_time:.2f}초")
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
        logger.error(f"❌ 실제 GPU 시나리오 테스트 실패: {e}")

if __name__ == "__main__":
    # GPU vs CPU 성능 비교
    compare_gpu_cpu_performance()
    
    # 배치 크기별 성능 테스트
    test_batch_size_performance()
    
    # 실제 GPU 시나리오 테스트
    test_real_world_gpu_scenario()
