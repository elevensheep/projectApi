#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
카테고리 처리 진행상황 모니터링 스크립트
"""

import time
import sys
import os

# app 폴더를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
sys.path.append(app_dir)

from services.database import MySQLDatabase
from datetime import datetime, timedelta

def monitor_progress():
    """카테고리 처리 진행상황 모니터링"""
    db = MySQLDatabase()
    
    print("🔍 카테고리 처리 진행상황 모니터링 시작...")
    print("=" * 60)
    
    try:
        # 1. 오늘 날짜의 뉴스 키워드 수 확인
        today = datetime.now().strftime("%Y-%m-%d")
        
        news_query = """
            SELECT news_category, COUNT(*) as count
            FROM tb_news_keyword 
            WHERE DATE(news_date) = %s
            GROUP BY news_category
        """
        
        news_results = db.fetch_query(news_query, (today,))
        
        print(f"📰 오늘({today}) 크롤링된 뉴스 키워드:")
        total_news = 0
        for category, count in news_results:
            print(f"   - {category}: {count}개")
            total_news += count
        
        print(f"   총 뉴스 키워드: {total_news}개")
        print()
        
        # 2. 추천 데이터 처리 현황 확인
        recommend_query = """
            SELECT n.news_category, COUNT(DISTINCT r.books_isbn) as book_count
            FROM tb_recommend r
            JOIN tb_news_keyword n ON r.news_id = n.news_id
            WHERE DATE(n.news_date) = %s
            GROUP BY n.news_category
        """
        
        recommend_results = db.fetch_query(recommend_query, (today,))
        
        print("📚 추천 도서 처리 현황:")
        total_books = 0
        for category, book_count in recommend_results:
            print(f"   - {category}: {book_count}권")
            total_books += book_count
        
        print(f"   총 추천 도서: {total_books}권")
        print()
        
        # 3. similarity_score 업데이트 현황
        score_query = """
            SELECT n.news_category, 
                   COUNT(*) as total_recommendations,
                   COUNT(r.similarity_score) as scored_recommendations,
                   AVG(r.similarity_score) as avg_score
            FROM tb_recommend r
            JOIN tb_news_keyword n ON r.news_id = n.news_id
            WHERE DATE(n.news_date) = %s
            GROUP BY n.news_category
        """
        
        score_results = db.fetch_query(score_query, (today,))
        
        print("📊 유사도 점수 처리 현황:")
        for category, total, scored, avg_score in score_results:
            progress = (scored / total * 100) if total > 0 else 0
            avg_score_str = f"{avg_score:.4f}" if avg_score else "N/A"
            print(f"   - {category}: {scored}/{total} ({progress:.1f}%) - 평균점수: {avg_score_str}")
        
        print()
        
        # 4. 최근 처리 시간 확인
        recent_query = """
            SELECT n.news_category, MAX(n.news_date) as last_processed
            FROM tb_news_keyword n
            WHERE DATE(n.news_date) = %s
            GROUP BY n.news_category
        """
        
        recent_results = db.fetch_query(recent_query, (today,))
        
        print("⏰ 최근 처리 시간:")
        for category, last_processed in recent_results:
            if last_processed:
                try:
                    # datetime.date를 datetime.datetime으로 변환
                    from datetime import date
                    if isinstance(last_processed, date):
                        last_processed = datetime.combine(last_processed, datetime.min.time())
                    time_diff = datetime.now() - last_processed
                    time_str = f"{time_diff.seconds//60}분 {time_diff.seconds%60}초 전"
                    print(f"   - {category}: {time_str}")
                except Exception as e:
                    print(f"   - {category}: 시간 계산 오류 - {e}")
        
        print()
        
        # 5. 전체 진행률 계산
        if total_news > 0 and total_books > 0:
            print("📈 전체 진행률:")
            print(f"   - 뉴스 키워드 처리: {total_news}개 완료")
            print(f"   - 도서 추천 생성: {total_books}권 완료")
            
            # 예상 완료 시간 (가정: 평균 1개 키워드당 30초)
            estimated_remaining = total_news * 30  # 초 단위
            estimated_completion = datetime.now() + timedelta(seconds=estimated_remaining)
            print(f"   - 예상 완료 시간: {estimated_completion.strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 모니터링 중 오류 발생: {e}")
    
    finally:
        db.close()

def continuous_monitor(interval=30):
    """지속적인 모니터링"""
    print(f"🔄 {interval}초마다 진행상황을 확인합니다. (Ctrl+C로 종료)")
    
    try:
        while True:
            print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 40)
            monitor_progress()
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n👋 모니터링을 종료합니다.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        continuous_monitor()
    else:
        monitor_progress()
