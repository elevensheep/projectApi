#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BERT 기반 추천 시스템
- 문맥적 유사도 계산
- 키워드 매칭
- 하이브리드 추천
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.bert_nlp import BertNLP
from services.database import PostgreSQLDatabase
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import logging
from typing import List, Dict, Tuple, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BertRecommendationSystem:
    """
    BERT 기반 향상된 추천 시스템
    """
    
    def __init__(self):
        """BERT 추천 시스템 초기화"""
        self.bert_nlp = BertNLP()
        self.db = PostgreSQLDatabase()
        logger.info("BERT 추천 시스템 초기화 완료")
    
    def recommend_books_by_context(self, news_data: dict) -> Dict[str, List[Tuple[str, float]]]:
        """
        문맥 기반 도서 추천
        
        Args:
            news_data: 뉴스 데이터 딕셔너리
            
        Returns:
            카테고리별 추천 도서 리스트
        """
        logger.info("🧠 문맥 기반 도서 추천 시작")
        
        # 모든 도서 설명 가져오기
        query = """
            SELECT books_isbn, books_title, books_description 
            FROM tb_books 
            WHERE books_description IS NOT NULL AND books_description != ''
        """
        books = self.db.fetch_query(query)
        
        book_data = {
            'isbn': [book[0] for book in books],
            'title': [book[1] for book in books],
            'description': [book[2] for book in books]
        }
        
        recommendations = {}
        
        for category, keywords in news_data.items():
            logger.info(f"📰 {category} 카테고리 처리 중...")
            
            category_recommendations = []
            
            for keyword in keywords:
                # 키워드를 포함한 문맥 생성
                context = f"{category} 관련 {keyword}에 대한 내용"
                
                # 문맥 기반 유사도 계산
                similarities = self._calculate_contextual_similarities(
                    context, book_data['description']
                )
                
                # 상위 추천 도서 선택
                top_books = self._get_top_recommendations(
                    similarities, book_data['isbn'], book_data['title'], 
                    threshold=0.3, top_k=5
                )
                
                category_recommendations.extend(top_books)
            
            # 중복 제거 및 점수 통합
            recommendations[category] = self._merge_recommendations(category_recommendations)
        
        return recommendations
    
    def recommend_books_by_keywords(self, news_data: dict) -> Dict[str, List[Tuple[str, float]]]:
        """
        키워드 기반 도서 추천
        
        Args:
            news_data: 뉴스 데이터 딕셔너리
            
        Returns:
            키워드별 추천 도서 리스트
        """
        logger.info("🔍 키워드 기반 도서 추천 시작")
        
        # 모든 도서 설명 가져오기
        query = """
            SELECT books_isbn, books_title, books_description 
            FROM tb_books 
            WHERE books_description IS NOT NULL AND books_description != ''
        """
        books = self.db.fetch_query(query)
        
        recommendations = defaultdict(list)
        
        for category, keywords in news_data.items():
            for keyword in keywords:
                # 키워드 추출
                keyword_tokens = self.bert_nlp.extract_keywords(keyword, top_k=5)
                
                for isbn, title, description in books:
                    if description:
                        # 도서 설명에서 키워드 추출
                        book_keywords = self.bert_nlp.extract_keywords(description, top_k=10)
                        
                        # 키워드 간 유사도 계산
                        keyword_similarity = 0
                        for kw1 in keyword_tokens:
                            for kw2 in book_keywords:
                                similarity = self.bert_nlp.calculate_word_similarity(kw1, kw2)
                                keyword_similarity = max(keyword_similarity, similarity)
                        
                        if keyword_similarity > 0.4:  # 키워드 유사도 임계값
                            recommendations[keyword].append((isbn, keyword_similarity))
        
        # 결과 정리
        final_recommendations = {}
        for keyword, recs in recommendations.items():
            # 유사도 순으로 정렬
            sorted_recs = sorted(recs, key=lambda x: x[1], reverse=True)
            final_recommendations[keyword] = sorted_recs[:5]
        
        return final_recommendations
    
    def recommend_books_by_clustering(self, news_data: dict, n_clusters: int = 5) -> Dict[str, List[Tuple[str, float]]]:
        """
        클러스터링 기반 도서 추천
        
        Args:
            news_data: 뉴스 데이터 딕셔너리
            n_clusters: 클러스터 개수
            
        Returns:
            클러스터별 추천 도서 리스트
        """
        logger.info("📊 클러스터링 기반 도서 추천 시작")
        
        # 모든 도서 설명 가져오기
        query = """
            SELECT books_isbn, books_title, books_description 
            FROM tb_books 
            WHERE books_description IS NOT NULL AND books_description != ''
        """
        books = self.db.fetch_query(query)
        
        descriptions = [desc for _, _, desc in books if desc]
        isbns = [isbn for isbn, _, desc in books if desc]
        titles = [title for _, title, desc in books if desc]
        
        # 도서 설명 클러스터링
        clusters = self.bert_nlp.cluster_texts(descriptions, n_clusters)
        
        recommendations = {}
        
        for category, keywords in news_data.items():
            for keyword in keywords:
                # 키워드가 속할 가장 적합한 클러스터 찾기
                best_cluster = self._find_best_cluster(keyword, clusters, descriptions)
                
                if best_cluster is not None:
                    # 해당 클러스터의 도서들 추천
                    cluster_books = clusters[best_cluster]
                    
                    for book_idx in cluster_books:
                        if book_idx < len(isbns):
                            isbn = isbns[book_idx]
                            # 클러스터 기반 점수 (0.6으로 고정)
                            recommendations.setdefault(keyword, []).append((isbn, 0.6))
        
        # 결과 정리
        final_recommendations = {}
        for keyword, recs in recommendations.items():
            # 중복 제거
            unique_recs = {}
            for isbn, score in recs:
                if isbn not in unique_recs or score > unique_recs[isbn]:
                    unique_recs[isbn] = score
            
            # 점수 순으로 정렬
            sorted_recs = sorted(unique_recs.items(), key=lambda x: x[1], reverse=True)
            final_recommendations[keyword] = sorted_recs[:5]
        
        return final_recommendations
    
    def hybrid_recommendation(self, news_data: dict) -> Dict[str, List[Tuple[str, float]]]:
        """
        하이브리드 추천 (문맥 + 키워드 + 클러스터링)
        
        Args:
            news_data: 뉴스 데이터 딕셔너리
            
        Returns:
            통합 추천 결과
        """
        logger.info("🔄 하이브리드 추천 시작")
        
        # 각 방법별 추천 결과
        context_recs = self.recommend_books_by_context(news_data)
        keyword_recs = self.recommend_books_by_keywords(news_data)
        cluster_recs = self.recommend_books_by_clustering(news_data)
        
        # 결과 통합
        hybrid_recs = defaultdict(dict)
        
        # 모든 키워드 수집
        all_keywords = set()
        for recs in [context_recs, keyword_recs, cluster_recs]:
            all_keywords.update(recs.keys())
        
        # 각 키워드별로 통합 점수 계산
        for keyword in all_keywords:
            keyword_scores = {}
            
            # 문맥 기반 점수 (가중치: 0.5)
            if keyword in context_recs:
                for isbn, score in context_recs[keyword]:
                    keyword_scores[isbn] = keyword_scores.get(isbn, 0) + score * 0.5
            
            # 키워드 기반 점수 (가중치: 0.3)
            if keyword in keyword_recs:
                for isbn, score in keyword_recs[keyword]:
                    keyword_scores[isbn] = keyword_scores.get(isbn, 0) + score * 0.3
            
            # 클러스터링 기반 점수 (가중치: 0.2)
            if keyword in cluster_recs:
                for isbn, score in cluster_recs[keyword]:
                    keyword_scores[isbn] = keyword_scores.get(isbn, 0) + score * 0.2
            
            # 최종 점수로 정렬
            sorted_scores = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
            hybrid_recs[keyword] = sorted_scores[:5]
        
        return dict(hybrid_recs)
    
    def save_recommendations_to_db(self, recommendations: Dict[str, List[Tuple[str, float]]], 
                                 method: str = "hybrid"):
        """
        추천 결과를 데이터베이스에 저장
        
        Args:
            recommendations: 추천 결과 딕셔너리
            method: 추천 방법
        """
        logger.info(f"💾 추천 결과 DB 저장 시작 (방법: {method})")
        
        try:
            # 기존 추천 데이터 삭제 (같은 방법으로 생성된 것들)
            delete_query = "DELETE FROM tb_recommend WHERE method = %s"
            self.db.execute_query(delete_query, (method,))
            
            # 새로운 추천 데이터 삽입
            insert_query = """
                INSERT IGNORE INTO tb_recommend 
                (news_keyword, books_isbn, similarity_score, method, created_at) 
                VALUES (%s, %s, %s, %s, NOW())
            """
            
            insert_count = 0
            for keyword, recs in recommendations.items():
                for isbn, score in recs:
                    self.db.execute_query(insert_query, (keyword, isbn, score, method))
                    insert_count += 1
            
            logger.info(f"✅ 추천 결과 저장 완료: {insert_count}개 레코드")
            
        except Exception as e:
            logger.error(f"❌ 추천 결과 저장 실패: {e}")
    
    def _calculate_contextual_similarities(self, context: str, descriptions: List[str]) -> List[float]:
        """문맥 기반 유사도 계산"""
        similarities = []
        for description in descriptions:
            if description:
                similarity = self.bert_nlp.calculate_contextual_similarity(context, description)
                similarities.append(similarity)
            else:
                similarities.append(0.0)
        return similarities
    
    def _get_top_recommendations(self, similarities: List[float], isbns: List[str], 
                               titles: List[str], threshold: float = 0.3, 
                               top_k: int = 5) -> List[Tuple[str, float, str]]:
        """상위 추천 도서 선택"""
        recommendations = []
        
        for i, similarity in enumerate(similarities):
            if similarity >= threshold and i < len(isbns):
                recommendations.append((isbns[i], similarity, titles[i]))
        
        # 점수 순으로 정렬
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations[:top_k]
    
    def _merge_recommendations(self, recommendations: List[Tuple[str, float, str]]) -> List[Tuple[str, float]]:
        """추천 결과 통합 및 중복 제거"""
        merged = {}
        
        for isbn, score, title in recommendations:
            if isbn not in merged or score > merged[isbn]:
                merged[isbn] = score
        
        # 점수 순으로 정렬
        sorted_recs = sorted(merged.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_recs[:5]  # 상위 10개 반환
    
    def _find_best_cluster(self, keyword: str, clusters: Dict[int, List[int]], 
                          descriptions: List[str]) -> Optional[int]:
        """키워드와 가장 유사한 클러스터 찾기"""
        best_cluster = None
        best_similarity = 0.0
        
        for cluster_id, book_indices in clusters.items():
            cluster_similarity = 0.0
            
            for book_idx in book_indices:
                if book_idx < len(descriptions):
                    description = descriptions[book_idx]
                    if description:
                        similarity = self.bert_nlp.calculate_contextual_similarity(keyword, description)
                        cluster_similarity += similarity
            
            # 클러스터 평균 유사도
            if book_indices:
                cluster_similarity /= len(book_indices)
                
                if cluster_similarity > best_similarity:
                    best_similarity = cluster_similarity
                    best_cluster = cluster_id
        
        return best_cluster
    
    def evaluate_recommendation_quality(self, method: str = "hybrid"):
        """추천 품질 평가"""
        logger.info(f"📈 추천 품질 평가 시작 (방법: {method})")
        
        try:
            # 추천 데이터 조회
            query = """
                SELECT news_keyword, books_isbn, similarity_score 
                FROM tb_recommend 
                WHERE method = %s 
                ORDER BY similarity_score DESC
            """
            recommendations = self.db.fetch_query(query, (method,))
            
            if not recommendations:
                logger.warning(f"평가할 추천 데이터가 없습니다: {method}")
                return
            
            # 통계 계산
            scores = [score for _, _, score in recommendations]
            
            stats = {
                'total_recommendations': len(recommendations),
                'average_score': np.mean(scores),
                'max_score': np.max(scores),
                'min_score': np.min(scores),
                'std_score': np.std(scores),
                'high_quality_count': len([s for s in scores if s >= 0.7]),
                'medium_quality_count': len([s for s in scores if 0.4 <= s < 0.7]),
                'low_quality_count': len([s for s in scores if s < 0.4])
            }
            
            logger.info(f"📊 추천 품질 평가 결과 ({method}):")
            logger.info(f"  - 총 추천 수: {stats['total_recommendations']}")
            logger.info(f"  - 평균 점수: {stats['average_score']:.3f}")
            logger.info(f"  - 최고 점수: {stats['max_score']:.3f}")
            logger.info(f"  - 최저 점수: {stats['min_score']:.3f}")
            logger.info(f"  - 고품질 추천: {stats['high_quality_count']}개")
            logger.info(f"  - 중품질 추천: {stats['medium_quality_count']}개")
            logger.info(f"  - 저품질 추천: {stats['low_quality_count']}개")
            
        except Exception as e:
            logger.error(f"❌ 추천 품질 평가 실패: {e}")
    
    def close(self):
        """리소스 정리"""
        self.db.close()
        logger.info("BERT 추천 시스템 종료")

def main():
    """메인 실행 함수"""
    logger.info("🚀 BERT 기반 도서 추천 시스템 시작")
    
    try:
        # 크롤러로 뉴스 데이터 가져오기
        from services.crowling import Crowling
        crawler = Crowling()
        
        # 뉴스 제목 가져오기 (BERT 시스템용)
        logger.info("📡 중앙일보 뉴스 제목 크롤링 중...")
        news_titles = crawler.get_news_titles()
        logger.info(f"✅ 뉴스 제목 크롤링 완료: {len(news_titles)}개 카테고리")
        
        # 각 카테고리별 제목 수 출력
        for category, titles in news_titles.items():
            logger.info(f"  - {category}: {len(titles)}개 제목")
        
        # BERT 추천 시스템 초기화
        recommender = BertRecommendationSystem()
        
        # 하이브리드 추천 실행 (뉴스 제목 사용)
        logger.info("🔄 BERT 기반 하이브리드 추천 시작...")
        recommendations = recommender.hybrid_recommendation(news_titles)
        
        # 결과 출력
        total_recommendations = 0
        for category, recs in recommendations.items():
            logger.info(f"\n📚 {category} 카테고리 추천 도서:")
            for isbn, score in recs[:5]:  # 상위 5개만 출력
                logger.info(f"   - {isbn}: {score:.4f}")
            total_recommendations += len(recs)
        
        logger.info(f"\n📊 총 추천 수: {total_recommendations}개")
        
        # DB에 저장
        recommender.save_recommendations_to_db(recommendations, "hybrid")
        
        # 품질 평가
        recommender.evaluate_recommendation_quality("hybrid")
        
    except Exception as e:
        logger.error(f"❌ BERT 추천 시스템 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'recommender' in locals():
            recommender.close()

if __name__ == "__main__":
    main() 