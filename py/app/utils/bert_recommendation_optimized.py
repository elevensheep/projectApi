#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
최적화된 BERT 기반 추천 시스템
- 배치 처리로 성능 향상
- 캐싱 시스템
- 병렬 처리
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.bert_nlp import BertNLP
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

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedBertRecommendationSystem:
    """
    최적화된 BERT 기반 추천 시스템
    """
    
    def __init__(self, cache_dir: str = "cache", batch_size: int = 64, max_workers: int = 4):
        """최적화된 BERT 추천 시스템 초기화"""
        self.bert_nlp = BertNLP()
        self.db = MySQLDatabase()
        self.cache_dir = cache_dir
        self.batch_size = batch_size
        self.max_workers = max_workers
        
        # 캐시 디렉토리 생성
        os.makedirs(cache_dir, exist_ok=True)
        
        # 임베딩 캐시
        self.embedding_cache = {}
        
        logger.info(f"🚀 최적화된 BERT 추천 시스템 초기화 완료 (배치크기: {batch_size}, 워커: {max_workers})")
    
    def recommend_books_by_context_optimized(self, news_data: dict) -> Dict[str, List[Tuple[str, float]]]:
        """
        최적화된 문맥 기반 도서 추천
        
        Args:
            news_data: 뉴스 데이터 딕셔너리
            
        Returns:
            카테고리별 추천 도서 리스트
        """
        start_time = time.time()
        logger.info("🧠 최적화된 문맥 기반 도서 추천 시작")
        
        # 1. 도서 데이터 배치 로드
        books_data = self._load_books_batch()
        logger.info(f"📚 {len(books_data['isbn'])}권의 도서 데이터 로드 완료")
        
        # 2. 도서 임베딩 배치 생성 (캐시 활용)
        book_embeddings = self._get_book_embeddings_batch(books_data['description'])
        logger.info(f"🔍 {len(book_embeddings)}개의 도서 임베딩 생성 완료")
        
        recommendations = {}
        
        # 3. 카테고리별 병렬 처리
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_category = {}
            
            for category, keywords in news_data.items():
                future = executor.submit(
                    self._process_category_optimized,
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
        
        return recommendations
    
    def _load_books_batch(self) -> Dict[str, List]:
        """도서 데이터 배치 로드"""
        query = """
            SELECT books_isbn, books_title, books_description 
            FROM tb_books 
            WHERE books_description IS NOT NULL AND books_description != ''
            LIMIT 1000  -- 성능을 위해 제한
        """
        books = self.db.fetch_query(query)
        
        return {
            'isbn': [book[0] for book in books],
            'title': [book[1] for book in books],
            'description': [book[2] for book in books]
        }
    
    def _get_book_embeddings_batch(self, descriptions: List[str]) -> List[np.ndarray]:
        """도서 임베딩 배치 생성 (캐시 활용)"""
        embeddings = []
        
        for i in range(0, len(descriptions), self.batch_size):
            batch_descriptions = descriptions[i:i+self.batch_size]
            batch_embeddings = []
            
            for desc in batch_descriptions:
                if desc:
                    # 캐시 키 생성
                    cache_key = self._get_cache_key(desc)
                    
                    if cache_key in self.embedding_cache:
                        # 캐시에서 로드
                        embedding = self.embedding_cache[cache_key]
                    else:
                        # 새로 생성
                        embedding = self.bert_nlp.get_bert_embedding(desc)
                        self.embedding_cache[cache_key] = embedding
                    
                    batch_embeddings.append(embedding)
                else:
                    batch_embeddings.append(np.zeros(768))
            
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def _process_category_optimized(self, category: str, keywords: List[str], 
                                  book_embeddings: List[np.ndarray], 
                                  books_data: Dict[str, List]) -> List[Tuple[str, float]]:
        """카테고리별 최적화된 처리"""
        category_recommendations = []
        
        for keyword in keywords:
            # 키워드 임베딩 생성
            context = f"{category} 관련 {keyword}에 대한 내용"
            context_embedding = self.bert_nlp.get_bert_embedding(context)
            
            # 배치 유사도 계산
            similarities = self._calculate_similarities_batch(context_embedding, book_embeddings)
            
            # 상위 추천 도서 선택
            top_books = self._get_top_recommendations_optimized(
                similarities, books_data['isbn'], books_data['title'], 
                threshold=0.3, top_k=5
            )
            
            category_recommendations.extend(top_books)
        
        # 중복 제거 및 점수 통합
        return self._merge_recommendations_optimized(category_recommendations)
    
    def _calculate_similarities_batch(self, query_embedding: np.ndarray, 
                                    book_embeddings: List[np.ndarray]) -> List[float]:
        """배치 유사도 계산"""
        similarities = []
        
        for book_embedding in book_embeddings:
            similarity = cosine_similarity([query_embedding], [book_embedding])[0][0]
            similarities.append(float(similarity))
        
        return similarities
    
    def _get_top_recommendations_optimized(self, similarities: List[float], 
                                         isbns: List[str], titles: List[str], 
                                         threshold: float = 0.3, 
                                         top_k: int = 5) -> List[Tuple[str, float, str]]:
        """최적화된 상위 추천 도서 선택"""
        # numpy 배열로 변환하여 빠른 정렬
        similarities_array = np.array(similarities)
        indices = np.argsort(similarities_array)[::-1]  # 내림차순 정렬
        
        recommendations = []
        for idx in indices:
            if similarities_array[idx] >= threshold and len(recommendations) < top_k:
                recommendations.append((isbns[idx], similarities_array[idx], titles[idx]))
        
        return recommendations
    
    def _merge_recommendations_optimized(self, recommendations: List[Tuple[str, float, str]]) -> List[Tuple[str, float]]:
        """최적화된 추천 결과 통합"""
        merged = {}
        
        for isbn, score, title in recommendations:
            if isbn not in merged or score > merged[isbn]:
                merged[isbn] = score
        
        # 점수 순으로 정렬
        sorted_recs = sorted(merged.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_recs[:10]  # 상위 10개 반환
    
    def _get_cache_key(self, text: str) -> str:
        """캐시 키 생성"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def save_cache(self):
        """임베딩 캐시 저장"""
        cache_file = os.path.join(self.cache_dir, "embedding_cache.pkl")
        with open(cache_file, 'wb') as f:
            pickle.dump(self.embedding_cache, f)
        logger.info(f"💾 임베딩 캐시 저장 완료: {len(self.embedding_cache)}개")
    
    def load_cache(self):
        """임베딩 캐시 로드"""
        cache_file = os.path.join(self.cache_dir, "embedding_cache.pkl")
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                self.embedding_cache = pickle.load(f)
            logger.info(f"📂 임베딩 캐시 로드 완료: {len(self.embedding_cache)}개")
    
    def clear_cache(self):
        """캐시 초기화"""
        self.embedding_cache.clear()
        cache_file = os.path.join(self.cache_dir, "embedding_cache.pkl")
        if os.path.exists(cache_file):
            os.remove(cache_file)
        logger.info("🗑️ 캐시 초기화 완료")
    
    def close(self):
        """리소스 정리"""
        self.save_cache()
        self.db.close()
        logger.info("🔚 최적화된 BERT 추천 시스템 종료")

def main():
    """메인 실행 함수"""
    logger.info("🚀 최적화된 BERT 추천 시스템 시작")
    
    try:
        # 크롤러로 뉴스 데이터 가져오기
        from services.crowling import Crowling
        crawler = Crowling()
        
        # 뉴스 제목 가져오기
        logger.info("📡 중앙일보 뉴스 제목 크롤링 중...")
        news_titles = crawler.get_news_titles()
        logger.info(f"✅ 뉴스 제목 크롤링 완료: {len(news_titles)}개 카테고리")
        
        # 최적화된 BERT 추천 시스템 초기화
        recommender = OptimizedBertRecommendationSystem(
            batch_size=64,  # 배치 크기 증가
            max_workers=4   # 병렬 처리 워커 수
        )
        
        # 캐시 로드
        recommender.load_cache()
        
        # 최적화된 추천 실행
        logger.info("🔄 최적화된 BERT 추천 시작...")
        start_time = time.time()
        
        recommendations = recommender.recommend_books_by_context_optimized(news_titles)
        
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
        recommender.save_recommendations_to_db(recommendations, "optimized_bert")
        
    except Exception as e:
        logger.error(f"❌ 최적화된 BERT 추천 시스템 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'recommender' in locals():
            recommender.close()

if __name__ == "__main__":
    main()
