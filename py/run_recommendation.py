#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
추천 시스템 실행 스크립트
"""

import sys
import os

# app 폴더를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
sys.path.append(app_dir)

from services.crowling import Crowling
from utils.recommendation_runner import recommend_books_by_keywords_enhanced

def main():
    print("🚀 추천 시스템 실행 시작...")
    
    try:
        # 크롤러 초기화
        crawler = Crowling()
        
        # 뉴스 데이터 크롤링
        print("📡 중앙일보 뉴스 키워드 크롤링 중...")
        news_data = crawler.wordExtraction()
        print("✅ 키워드 추출 완료:", news_data)
        
        # 추천 시스템 실행
        print("📘 향상된 추천 도서 추출 및 저장 중...")
        recommend_books_by_keywords_enhanced(news_data)
        print("✅ 향상된 추천 완료 및 DB 저장 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
