#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
오늘자 데이터 중복 체크 및 건너뛰기 기능
"""

import time
from datetime import datetime, date
from .database import MySQLDatabase

class DuplicateDataChecker:
    def __init__(self):
        self.db = MySQLDatabase()
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def check_today_data_exists(self) -> dict:
        """오늘자 데이터 존재 여부 확인"""
        result = {
            'exists': False,
            'news_keywords': 0,
            'recommendations': 0,
            'categories': [],
            'details': {}
        }
        
        try:
            # 1. 오늘 날짜의 뉴스 키워드 확인
            news_query = """
                SELECT news_category, COUNT(*) as count
                FROM tb_news_keyword 
                WHERE DATE(news_date) = %s
                GROUP BY news_category
            """
            
            news_results = self.db.fetch_query(news_query, (self.today,))
            
            if news_results:
                result['exists'] = True
                result['categories'] = [category for category, _ in news_results]
                
                for category, count in news_results:
                    result['news_keywords'] += count
                    result['details'][category] = {'news_keywords': count, 'recommendations': 0}
            
            # 2. 오늘 날짜의 추천 데이터 확인
            if result['exists']:
                recommend_query = """
                    SELECT n.news_category, COUNT(DISTINCT r.books_isbn) as book_count
                    FROM tb_recommend r
                    JOIN tb_news_keyword n ON r.news_id = n.news_id
                    WHERE DATE(n.news_date) = %s
                    GROUP BY n.news_category
                """
                
                recommend_results = self.db.fetch_query(recommend_query, (self.today,))
                
                for category, book_count in recommend_results:
                    result['recommendations'] += book_count
                    if category in result['details']:
                        result['details'][category]['recommendations'] = book_count
            
            return result
            
        except Exception as e:
            print(f"❌ 데이터 확인 중 오류 발생: {e}")
            return result
    
    def should_skip_processing(self, min_news_keywords: int = 10, min_recommendations: int = 50) -> bool:
        """처리를 건너뛸지 결정"""
        data_status = self.check_today_data_exists()
        
        if not data_status['exists']:
            print(f"✅ 오늘({self.today}) 데이터가 없습니다. 처리 진행합니다.")
            return False
        
        print(f"🔍 오늘({self.today}) 데이터 확인 결과:")
        print(f"   - 뉴스 키워드: {data_status['news_keywords']}개")
        print(f"   - 추천 도서: {data_status['recommendations']}권")
        print(f"   - 처리된 카테고리: {', '.join(data_status['categories'])}")
        
        # 상세 정보 출력
        for category, details in data_status['details'].items():
            print(f"     • {category}: 뉴스 {details['news_keywords']}개, 추천 {details['recommendations']}권")
        
        # 기준값과 비교
        if (data_status['news_keywords'] >= min_news_keywords and 
            data_status['recommendations'] >= min_recommendations):
            print(f"✅ 충분한 데이터가 이미 존재합니다. (기준: 뉴스 {min_news_keywords}개, 추천 {min_recommendations}권)")
            print("⏭️  처리를 건너뜁니다.")
            return True
        else:
            print(f"⚠️  데이터가 부족합니다. (기준: 뉴스 {min_news_keywords}개, 추천 {min_recommendations}권)")
            print("🔄 처리를 진행합니다.")
            return False
    
    def force_reprocess(self):
        """강제 재처리 (오늘자 데이터 삭제)"""
        try:
            print(f"🗑️  오늘({self.today}) 데이터를 삭제하고 재처리를 진행합니다...")
            
            # 1. 추천 데이터 삭제
            delete_recommend_query = """
                DELETE r FROM tb_recommend r
                JOIN tb_news_keyword n ON r.news_id = n.news_id
                WHERE DATE(n.news_date) = %s
            """
            recommend_deleted = self.db.execute_query(delete_recommend_query, (self.today,))
            
            # 2. 뉴스 키워드 삭제
            delete_news_query = """
                DELETE FROM tb_news_keyword 
                WHERE DATE(news_date) = %s
            """
            news_deleted = self.db.execute_query(delete_news_query, (self.today,))
            
            print(f"✅ 삭제 완료: 추천 데이터 {recommend_deleted}개, 뉴스 키워드 {news_deleted}개")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 삭제 중 오류 발생: {e}")
            return False
    
    def close(self):
        """데이터베이스 연결 종료"""
        self.db.close()
