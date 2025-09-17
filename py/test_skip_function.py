#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
건너뛰기 기능 테스트 스크립트
"""

import sys
import os

# app 폴더를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
sys.path.append(app_dir)

from services.duplicate_checker import DuplicateDataChecker

def test_skip_function():
    """건너뛰기 기능 테스트"""
    print("🧪 건너뛰기 기능 테스트 시작")
    print("=" * 50)
    
    checker = DuplicateDataChecker()
    
    try:
        # 1. 현재 데이터 상태 확인
        print("1️⃣ 현재 데이터 상태 확인:")
        data_status = checker.check_today_data_exists()
        
        if data_status['exists']:
            print(f"   ✅ 오늘자 데이터 존재: {data_status['news_keywords']}개 뉴스, {data_status['recommendations']}개 추천")
            print(f"   📊 카테고리: {', '.join(data_status['categories'])}")
        else:
            print("   ❌ 오늘자 데이터 없음")
        
        print()
        
        # 2. 건너뛰기 판단 테스트
        print("2️⃣ 건너뛰기 판단 테스트:")
        should_skip = checker.should_skip_processing()
        print(f"   결과: {'건너뛰기' if should_skip else '처리 진행'}")
        
        print()
        
        # 3. 강제 재처리 옵션 테스트
        if should_skip:
            print("3️⃣ 강제 재처리 옵션:")
            print("   현재 건너뛰기 상태입니다.")
            print("   강제 재처리를 원하시면 다음 명령을 실행하세요:")
            print("   python check_and_skip_duplicate.py")
        
        print()
        
        # 4. 상세 정보 출력
        print("4️⃣ 상세 정보:")
        for category, details in data_status['details'].items():
            print(f"   • {category}: 뉴스 {details['news_keywords']}개, 추천 {details['recommendations']}권")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
    
    finally:
        checker.close()

def test_with_custom_threshold():
    """사용자 정의 임계값으로 테스트"""
    print("\n🔧 사용자 정의 임계값 테스트")
    print("=" * 30)
    
    checker = DuplicateDataChecker()
    
    try:
        # 낮은 임계값으로 테스트 (더 엄격한 조건)
        print("낮은 임계값 테스트 (뉴스 5개, 추천 20개):")
        should_skip_strict = checker.should_skip_processing(min_news_keywords=5, min_recommendations=20)
        print(f"   결과: {'건너뛰기' if should_skip_strict else '처리 진행'}")
        
        print()
        
        # 높은 임계값으로 테스트 (더 관대한 조건)
        print("높은 임계값 테스트 (뉴스 20개, 추천 100개):")
        should_skip_lenient = checker.should_skip_processing(min_news_keywords=20, min_recommendations=100)
        print(f"   결과: {'건너뛰기' if should_skip_lenient else '처리 진행'}")
        
    except Exception as e:
        print(f"❌ 사용자 정의 테스트 중 오류 발생: {e}")
    
    finally:
        checker.close()

if __name__ == "__main__":
    test_skip_function()
    test_with_custom_threshold()
    
    print("\n📋 테스트 완료!")
    print("\n💡 사용법:")
    print("   • 기본 건너뛰기 체크: python check_and_skip_duplicate.py")
    print("   • 진행상황 모니터링: python monitor_progress.py")
    print("   • GPU 추천 시스템: python app/utils/bert_recommendation_gpu.py")
