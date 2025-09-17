#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPU 최적화된 BERT 기반 추천 시스템
- CUDA 가속
- 배치 처리 최적화
- 메모리 효율성
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.bert_nlp_gpu_optimized import GPUBertNLP
from services.database import MySQLDatabase
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import logging
from typing import List, Dict, Tuple, Optional
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
import hashlib
import torch

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPUBertRecommendationSystem:
    """
    GPU 최적화된 BERT 기반 추천 시스템
    """
    
    def __init__(self, cache_dir: str = "cache", batch_size: int = 128, max_workers: int = 2):
        """GPU 최적화된 BERT 추천 시스템 초기화"""
        self.bert_nlp = GPUBertNLP()
        self.db = MySQLDatabase()
        self.cache_dir = cache_dir
        self.batch_size = batch_size
        self.max_workers = max_workers
        
        # GPU 사용 가능 여부 확인
        self.use_gpu = torch.cuda.is_available()
        
        # 캐시 디렉토리 생성
        os.makedirs(cache_dir, exist_ok=True)
        
        # 임베딩 캐시
        self.embedding_cache = {}
        
        logger.info(f"🚀 GPU 최적화된 BERT 추천 시스템 초기화 완료")
        logger.info(f"   - GPU 사용: {self.use_gpu}")
        logger.info(f"   - 배치 크기: {batch_size}")
        logger.info(f"   - 워커 수: {max_workers}")
        
        # GPU 통계 출력
        gpu_stats = self.bert_nlp.get_gpu_stats()
        logger.info(f"   - GPU 통계: {gpu_stats}")
    
    def recommend_books_by_context_gpu(self, news_data: dict) -> Dict[str, List[Tuple[str, float]]]:
        """
        GPU 최적화된 문맥 기반 도서 추천
        
        Args:
            news_data: 뉴스 데이터 딕셔너리
            
        Returns:
            카테고리별 추천 도서 리스트
        """
        start_time = time.time()
        logger.info("🧠 GPU 최적화된 문맥 기반 도서 추천 시작")
        
        # 1. 도서 데이터 배치 로드
        books_data = self._load_books_batch()
        logger.info(f"📚 {len(books_data['isbn'])}권의 도서 데이터 로드 완료")
        
        # 2. 도서 임베딩 GPU 배치 생성 (캐시 활용)
        book_embeddings = self._get_book_embeddings_gpu_batch(books_data['description'])
        logger.info(f"🔍 {len(book_embeddings)}개의 도서 임베딩 생성 완료")
        
        recommendations = {}
        
        # 3. 카테고리별 병렬 처리 (GPU 사용 시 워커 수 줄임)
        if self.use_gpu:
            # GPU 사용 시 메모리 경합을 피하기 위해 워커 수 줄임
            actual_workers = min(self.max_workers, 2)
        else:
            actual_workers = self.max_workers
        
        with ThreadPoolExecutor(max_workers=actual_workers) as executor:
            future_to_category = {}
            
            for category, keywords in news_data.items():
                future = executor.submit(
                    self._process_category_gpu,
                    category, keywords, book_embeddings, books_data
                )
                future_to_category[future] = category
            
            # 결과 수집
            for future in as_completed(future_to_category):
                category = future_to_category[future]
                try:
                    category_recommendations = future.result()
                    recommendations[category] = category_recommendations
                    logger.info(f"✅ {category} 카테고리 처리 완료: {len(category_recommendations)}권")
                except Exception as e:
                    logger.error(f"❌ {category} 카테고리 처리 실패: {e}")
                    recommendations[category] = []
        
        total_time = time.time() - start_time
        logger.info(f"🎉 전체 추천 완료: {total_time:.2f}초")
        
        # GPU 통계 출력
        final_gpu_stats = self.bert_nlp.get_gpu_stats()
        logger.info(f"💾 최종 GPU 통계: {final_gpu_stats}")
        
        return recommendations
    
    def _load_books_batch(self) -> Dict[str, List]:
        """도서 데이터 배치 로드"""
        query = """
            SELECT books_isbn, books_title, books_description 
            FROM tb_books 
            WHERE books_description IS NOT NULL AND books_description != ''
            LIMIT 2000  -- GPU 사용 시 더 많은 데이터 처리 가능
        """
        books = self.db.fetch_query(query)
        
        return {
            'isbn': [book[0] for book in books],
            'title': [book[1] for book in books],
            'description': [book[2] for book in books]
        }
    
    def _get_book_embeddings_gpu_batch(self, descriptions: List[str]) -> List[np.ndarray]:
        """도서 임베딩 GPU 배치 생성 (캐시 활용)"""
        embeddings = []
        
        # GPU 메모리에 따른 배치 크기 조정
        if self.use_gpu:
            gpu_stats = self.bert_nlp.get_gpu_stats()
            gpu_memory_gb = gpu_stats['total_memory_mb'] / 1024
            
            if gpu_memory_gb < 4:  # 4GB 미만
                batch_size = min(self.batch_size, 32)
            elif gpu_memory_gb < 8:  # 8GB 미만
                batch_size = min(self.batch_size, 64)
            else:  # 8GB 이상
                batch_size = min(self.batch_size, 128)
        else:
            batch_size = min(self.batch_size, 32)
        
        logger.info(f"📦 GPU 배치 처리 시작 (배치 크기: {batch_size})")
        
        for i in range(0, len(descriptions), batch_size):
            batch_descriptions = descriptions[i:i+batch_size]
            
            # GPU 배치 임베딩 생성
            batch_embeddings = self.bert_nlp.get_embeddings_batch_gpu(batch_descriptions, batch_size)
            embeddings.extend(batch_embeddings)
            
            # 진행률 출력
            progress = (i + batch_size) / len(descriptions) * 100
            logger.info(f"   진행률: {min(progress, 100):.1f}%")
        
        return embeddings
    
    def _process_category_gpu(self, category: str, keywords: List[str], 
                            book_embeddings: List[np.ndarray], 
                            books_data: Dict[str, List]) -> List[Tuple[str, float]]:
        """카테고리별 GPU 최적화된 처리"""
        category_recommendations = []
        
        for keyword in keywords:
            # 키워드 임베딩 생성
            context = f"{category} 관련 {keyword}에 대한 내용"
            context_embedding = self.bert_nlp.get_bert_embedding_gpu(context)
            
            # GPU 배치 유사도 계산
            similarities = self._calculate_similarities_gpu_batch(context_embedding, book_embeddings)
            
            # 상위 추천 도서 선택
            top_books = self._get_top_recommendations_gpu(
                similarities, books_data['isbn'], books_data['title'], 
                threshold=0.3, top_k=5
            )
            
            category_recommendations.extend(top_books)
        
        # 중복 제거 및 점수 통합
        return self._merge_recommendations_gpu(category_recommendations)
    
    def _calculate_similarities_gpu_batch(self, query_embedding: np.ndarray, 
                                        book_embeddings: List[np.ndarray]) -> List[float]:
        """GPU 배치 유사도 계산"""
        if self.use_gpu and len(book_embeddings) > 1000:
            # GPU에서 대용량 유사도 계산
            return self.bert_nlp._calculate_similarities_gpu(query_embedding, book_embeddings)
        else:
            # CPU에서 계산 (소용량 데이터)
            similarities = []
            for book_embedding in book_embeddings:
                similarity = cosine_similarity([query_embedding], [book_embedding])[0][0]
                similarities.append(float(similarity))
            return similarities
    
    def _get_top_recommendations_gpu(self, similarities: List[float], 
                                   isbns: List[str], titles: List[str], 
                                   threshold: float = 0.3, 
                                   top_k: int = 5) -> List[Tuple[str, float, str]]:
        """GPU 최적화된 상위 추천 도서 선택"""
        # numpy 배열로 변환하여 빠른 정렬
        similarities_array = np.array(similarities)
        indices = np.argsort(similarities_array)[::-1]  # 내림차순 정렬
        
        recommendations = []
        for idx in indices:
            if similarities_array[idx] >= threshold and len(recommendations) < top_k:
                recommendations.append((isbns[idx], similarities_array[idx], titles[idx]))
        
        return recommendations
    
    def _merge_recommendations_gpu(self, recommendations: List[Tuple[str, float, str]]) -> List[Tuple[str, float]]:
        """GPU 최적화된 추천 결과 통합"""
        merged = {}
        
        for isbn, score, title in recommendations:
            if isbn not in merged or score > merged[isbn]:
                merged[isbn] = score
        
        # 점수 순으로 정렬
        sorted_recs = sorted(merged.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_recs[:10]  # 상위 10개 반환
    
    def save_recommendations_to_db(self, recommendations: Dict[str, List[Tuple[str, float]]], 
                                 method: str = "gpu_bert"):
        """추천 결과를 DB에 저장"""
        logger.info(f"💾 추천 결과 DB 저장 시작 (방법: {method})")
        
        try:
            # 기존 추천 데이터 삭제
            delete_query = "DELETE FROM tb_recommend WHERE method = %s"
            self.db.execute_query(delete_query, (method,))
            
            # 새로운 추천 데이터 삽입
            insert_query = """
                INSERT INTO tb_recommend (news_keyword, books_isbn, similarity_score, method, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            total_inserted = 0
            for category, recs in recommendations.items():
                for isbn, score in recs:
                    self.db.execute_query(insert_query, (
                        category, isbn, score, method, datetime.now()
                    ))
                    total_inserted += 1
            
            logger.info(f"✅ 추천 결과 DB 저장 완료: {total_inserted}개")
            
        except Exception as e:
            logger.error(f"❌ 추천 결과 DB 저장 실패: {e}")
    
    def _get_cache_key(self, text: str) -> str:
        """캐시 키 생성"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def save_cache(self):
        """임베딩 캐시 저장"""
        cache_file = os.path.join(self.cache_dir, "gpu_embedding_cache.pkl")
        with open(cache_file, 'wb') as f:
            pickle.dump(self.embedding_cache, f)
        logger.info(f"💾 GPU 임베딩 캐시 저장 완료: {len(self.embedding_cache)}개")
    
    def load_cache(self):
        """임베딩 캐시 로드"""
        cache_file = os.path.join(self.cache_dir, "gpu_embedding_cache.pkl")
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                self.embedding_cache = pickle.load(f)
            logger.info(f"📂 GPU 임베딩 캐시 로드 완료: {len(self.embedding_cache)}개")
    
    def clear_cache(self):
        """캐시 초기화"""
        self.embedding_cache.clear()
        cache_file = os.path.join(self.cache_dir, "gpu_embedding_cache.pkl")
        if os.path.exists(cache_file):
            os.remove(cache_file)
        logger.info("🗑️ GPU 캐시 초기화 완료")
    
    def close(self):
        """리소스 정리"""
        self.save_cache()
        self.bert_nlp.save_cache()
        self.bert_nlp.clear_gpu_cache()
        self.db.close()
        logger.info("🔚 GPU 최적화된 BERT 추천 시스템 종료")

def main():
    """메인 실행 함수"""
    logger.info("🚀 GPU 최적화된 BERT 추천 시스템 시작")
    
    try:
        # 중복 데이터 체크
        from services.duplicate_checker import DuplicateDataChecker
        
        checker = DuplicateDataChecker()
        should_skip = checker.should_skip_processing()
        checker.close()
        
        if should_skip:
            logger.info("⏭️  오늘자 데이터가 이미 존재하여 처리를 건너뜁니다.")
            return
        
        # 크롤러로 뉴스 데이터 가져오기
        from services.crowling import Crowling
        crawler = Crowling()
        
        # 뉴스 제목 가져오기
        logger.info("📡 중앙일보 뉴스 제목 크롤링 중...")
        news_titles = crawler.get_news_titles()
        logger.info(f"✅ 뉴스 제목 크롤링 완료: {len(news_titles)}개 카테고리")
        
        # GPU 최적화된 BERT 추천 시스템 초기화
        recommender = GPUBertRecommendationSystem(
            batch_size=128,  # GPU 사용 시 더 큰 배치 크기
            max_workers=2    # GPU 사용 시 워커 수 줄임
        )
        
        # 캐시 로드
        recommender.load_cache()
        
        # GPU 최적화된 추천 실행
        logger.info("🔄 GPU 최적화된 BERT 추천 시작...")
        start_time = time.time()
        
        recommendations = recommender.recommend_books_by_context_gpu(news_titles)
        
        total_time = time.time() - start_time
        logger.info(f"⏱️ 총 처리 시간: {total_time:.2f}초")
        
        # 결과 출력
        total_recommendations = 0
        for category, recs in recommendations.items():
            logger.info(f"\n📚 {category} 카테고리 추천 도서:")
            for isbn, score in recs[:5]:  # 상위 5개만 출력
                logger.info(f"   - {isbn}: {score:.4f}")
            total_recommendations += len(recs)
        
        logger.info(f"\n📊 총 추천 수: {total_recommendations}개")
        
        # DB에 저장
        recommender.save_recommendations_to_db(recommendations, "gpu_bert")
        
    except Exception as e:
        logger.error(f"❌ GPU 최적화된 BERT 추천 시스템 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'recommender' in locals():
            recommender.close()

if __name__ == "__main__":
    main()
