#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FastAPI 메인 애플리케이션
- 성능 최적화
- 로깅 시스템
- 에러 핸들링
- 설정 관리
"""

import sys
import os

# 현재 app 폴더를 PYTHONPATH에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from api.endpoints import router
from fastapi.middleware.cors import CORSMiddleware
from services.crowling import Crowling
from utils.recommendation_runner import recommend_books_by_keywords

app = FastAPI(title="News-Book Recommender API")

origins = [
    "http://localhost:3000",  # React 개발 서버 포트
    "http://127.0.0.1:3000"
]

# CORS 미들웨어 등록
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # 허용할 origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("🚀 서버 시작과 함께 추천 시스템 실행 중...")
    try:
        # 중복 데이터 체크
        from services.duplicate_checker import DuplicateDataChecker
        
        checker = DuplicateDataChecker()
        should_skip = checker.should_skip_processing()
        checker.close()
        
        if should_skip:
            print("⏭️  오늘자 데이터가 이미 존재하여 처리를 건너뜁니다.")
            print("✅ 추천 시스템 초기화 완료 (건너뛰기)")
            return
        
        # 정상 처리 진행
        crawler = Crowling()
        news_data = crawler.wordExtraction()  # ✅ 여기서 먼저 데이터 만들고
        recommend_books_by_keywords(news_data)  # ✅ 그걸 넣어서 실행
        print("✅ 추천 시스템 초기화 완료")
    except Exception as e:
        print(f"❌ 추천 시스템 초기화 실패: {e}")
        # 초기화 실패해도 서버는 시작
        pass

@app.get("/health")
async def health_check():
    """헬스체크"""
    return {"status": "healthy", "message": "FastAPI 서버가 정상적으로 실행 중입니다."}

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    # 개발 모드 비활성화 (reload=False)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
