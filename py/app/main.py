import sys
import os

# 현재 app 폴더를 PYTHONPATH에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from app.api.endpoints import router
from fastapi.middleware.cors import CORSMiddleware
from app.services.crowling import Crowling
from app.utils.recommendation_runner import recommend_books_by_keywords

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
    crawler = Crowling()
    news_data = crawler.wordExtraction()  # ✅ 여기서 먼저 데이터 만들고
    recommend_books_by_keywords(news_data)  # ✅ 그걸 넣어서 실행
    
app.include_router(router, prefix="/api")
