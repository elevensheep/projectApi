#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
오늘자 데이터 중복 체크 및 건너뛰기 기능
"""

import time
from datetime import datetime, date
from ..core.database import PostgreSQLDatabase

class DuplicateDataChecker:
    def __init__(self):
        self.db = PostgreSQLDatabase()
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
                    result['details'][category] = {
                        'news_keywords': count,
                        'recommendations': 0
                    }
            
            # 2. 오늘 날짜의 추천 데이터 확인
            recommend_query = """
                SELECT news_category, COUNT(*) as count
                FROM tb_recommend 
                WHERE DATE(recommend_date) = %s
                GROUP BY news_category
            """
            
            recommend_results = self.db.fetch_query(recommend_query, (self.today,))
            
            if recommend_results:
                for category, count in recommend_results:
                    result['recommendations'] += count
                    if category in result['details']:
                        result['details'][category]['recommendations'] = count
                    else:
                        result['details'][category] = {
                            'news_keywords': 0,
                            'recommendations': count
                        }
            
            return result
            
        except Exception as e:
            print(f"❌ 데이터 확인 중 오류: {e}")
            return result
    
    def should_skip_processing(self) -> bool:
        """처리 건너뛰기 여부 판단"""
        data_status = self.check_today_data_exists()
        
        if not data_status['exists']:
            return False
        
        # 기준값: 뉴스 키워드 10개 이상, 추천 도서 50권 이상
        min_news_keywords = 10
        min_recommendations = 50
        
        should_skip = (
            data_status['news_keywords'] >= min_news_keywords and
            data_status['recommendations'] >= min_recommendations
        )
        
        if should_skip:
            print(f"✅ 오늘자 데이터 충분: 뉴스 {data_status['news_keywords']}개, 추천 {data_status['recommendations']}개")
            print(f"📊 카테고리: {', '.join(data_status['categories'])}")
        else:
            print(f"⚠️ 오늘자 데이터 부족: 뉴스 {data_status['news_keywords']}개, 추천 {data_status['recommendations']}개")
            print("🔄 처리를 계속 진행합니다.")
        
        return should_skip
    
    def force_reprocess(self) -> bool:
        """강제 재처리 (오늘자 데이터 삭제)"""
        try:
            print("🗑️ 오늘자 데이터 삭제 중...")
            
            # 오늘 날짜의 추천 데이터 삭제
            delete_recommend_sql = """
                DELETE FROM tb_recommend 
                WHERE DATE(recommend_date) = %s
            """
            self.db.execute_query(delete_recommend_sql, (self.today,))
            
            # 오늘 날짜의 뉴스 키워드 삭제
            delete_news_sql = """
                DELETE FROM tb_news_keyword 
                WHERE DATE(news_date) = %s
            """
            self.db.execute_query(delete_news_sql, (self.today,))
            
            print("✅ 오늘자 데이터 삭제 완료")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 삭제 중 오류: {e}")
            return False
    
    def close(self):
        """데이터베이스 연결 종료"""
        if hasattr(self.db, 'close'):
            self.db.close()
