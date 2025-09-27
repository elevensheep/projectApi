#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BERT 기반 추천 시스템 실행 스크립트
"""

import sys
import os
import torch

# app 폴더를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
py_dir = os.path.dirname(current_dir)
app_dir = os.path.join(py_dir, 'app')
sys.path.append(app_dir)

from core.crowling import Crowling
from utils.duplicate_checker import DuplicateDataChecker

def main():
    print("🚀 BERT 기반 추천 시스템 실행 시작...")
    print(f"🔧 GPU 사용 가능: {torch.cuda.is_available()}")
    
    try:
        # 중복 데이터 체크
        print("🔍 오늘자 데이터 중복 체크 중...")
        checker = DuplicateDataChecker()
        should_skip = checker.should_skip_processing()
        
        if should_skip:
            print("⏭️ 오늘자 데이터가 이미 존재합니다. 건너뜁니다.")
            print("💡 강제 재처리를 원하시면 데이터베이스를 확인해주세요.")
            return
        
        # 크롤러 초기화
        crawler = Crowling()
        
        # 뉴스 데이터 크롤링
        print("📡 중앙일보 뉴스 키워드 크롤링 중...")
        news_data = crawler.wordExtraction()
        print("✅ 키워드 추출 완료:", news_data)
        
        # BERT 추천 시스템 실행
        if torch.cuda.is_available():
            print("🚀 GPU 최적화된 BERT 추천 시스템 실행 중...")
            from core.recommendation.bert_recommendation_gpu import GPUBertRecommendationSystem
            
            bert_system = GPUBertRecommendationSystem()
            bert_system.recommend_books_by_context(news_data)
        else:
            print("🚀 CPU BERT 추천 시스템 실행 중...")
            from core.recommendation.bert_recommendation import BertRecommendationSystem
            
            bert_system = BertRecommendationSystem()
            bert_system.recommend_books_by_context(news_data)
        
        print("✅ BERT 기반 추천 완료 및 DB 저장 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
