#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FastAPI 엔드포인트 정의
- 추천 시스템 API
- 모델 시각화 API
- 캐싱 시스템
"""

import logging
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, Path, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import mysql.connector

# 상대 경로로 import 수정
from services.database import MySQLDatabase
from services.nlp import Nlp

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic 모델
class BookResponse(BaseModel):
    """책 정보 응답 모델"""
    books_isbn: str = Field(..., description="책 ISBN")
    news_category: str = Field(..., description="뉴스 카테고리")
    books_img: Optional[str] = Field(None, description="책 이미지 URL")
    books_description: Optional[str] = Field(None, description="책 설명")
    books_title: str = Field(..., description="책 제목")
    books_publisher: Optional[str] = Field(None, description="출판사")
    similarity_score: Optional[float] = Field(None, description="유사도 점수")

class RecommendationResponse(BaseModel):
    """추천 응답 모델"""
    total: int = Field(..., description="전체 책 수")
    page: int = Field(..., description="현재 페이지")
    limit: int = Field(..., description="페이지당 항목 수")
    total_pages: int = Field(..., description="전체 페이지 수")
    books: List[BookResponse] = Field(..., description="책 목록")
    cache_hit: bool = Field(False, description="캐시 히트 여부")

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: bool = Field(True, description="에러 여부")
    message: str = Field(..., description="에러 메시지")
    details: Optional[Dict[str, Any]] = Field(None, description="상세 정보")

# 캐시 시스템
recommendation_cache: Dict[str, Dict[str, Any]] = {}
cache_timestamps: Dict[str, float] = {}
CACHE_TTL = 3600  # 1시간

def get_cache_key(category: str, date: Optional[str], page: int, limit: int) -> str:
    """캐시 키 생성"""
    return f"{category}:{date or 'all'}:{page}:{limit}"

def is_cache_valid(cache_key: str) -> bool:
    """캐시 유효성 검사"""
    if cache_key not in cache_timestamps:
        return False
    return time.time() - cache_timestamps[cache_key] < CACHE_TTL

def get_cached_data(cache_key: str) -> Optional[Dict[str, Any]]:
    """캐시된 데이터 조회"""
    if is_cache_valid(cache_key):
        logger.info(f"📦 캐시 히트: {cache_key}")
        return recommendation_cache.get(cache_key)
    return None

def set_cached_data(cache_key: str, data: Dict[str, Any]):
    """데이터 캐싱"""
    recommendation_cache[cache_key] = data
    cache_timestamps[cache_key] = time.time()
    logger.info(f"💾 캐시 저장: {cache_key}")

# 데이터베이스 의존성
def get_database():
    """데이터베이스 연결 의존성"""
    db = MySQLDatabase()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/recommend/{category}",
    response_model=RecommendationResponse,
    summary="카테고리별 도서 추천",
    description="특정 카테고리의 뉴스 기반 도서 추천을 제공합니다.",
    responses={
        200: {"description": "성공적으로 추천 도서를 반환"},
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        404: {"model": ErrorResponse, "description": "카테고리를 찾을 수 없음"},
        500: {"model": ErrorResponse, "description": "서버 내부 오류"}
    }
)
async def get_recommendations(
    category: str = Path(..., description="뉴스 카테고리 (politics, sports, economic, society, world)"),
    date: Optional[str] = Query(None, alias="news_date", description="뉴스 날짜 (YYYY-MM-DD)"),
    page: int = Query(1, gt=0, le=1000, description="페이지 번호"),
    limit: int = Query(10, gt=0, le=100, description="페이지당 항목 수"),
    db: MySQLDatabase = Depends(get_database)
):
    """
    카테고리별 도서 추천 API
    
    - **category**: 뉴스 카테고리 (politics, sports, economic, society, world)
    - **date**: 뉴스 날짜 (선택사항, YYYY-MM-DD 형식)
    - **page**: 페이지 번호 (기본값: 1)
    - **limit**: 페이지당 항목 수 (기본값: 10, 최대: 100)
    """
    
    start_time = time.time()
    
    try:
        # 입력 검증 및 오타 수정
        valid_categories = ["politics", "sports", "economic", "society", "world"]
        
        # 오타 수정 (일반적인 오타들)
        category_fixes = {
            "ecomonic": "economic",
            "economy": "economic",
            "politic": "politics",
            "sport": "sports",
            "social": "society",
            "international": "world"
        }
        
        # 오타 수정 적용
        if category in category_fixes:
            original_category = category
            category = category_fixes[category]
            logger.info(f"🔧 카테고리 오타 수정: '{original_category}' → '{category}'")
        
        if category not in valid_categories:
            raise HTTPException(
                status_code=400,
                detail=f"유효하지 않은 카테고리입니다. 허용된 값: {', '.join(valid_categories)}"
            )
        
        # 날짜 형식 검증
        if date:
            try:
                time.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요."
                )
        
        # 캐시 확인
        cache_key = get_cache_key(category, date, page, limit)
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            cached_data["cache_hit"] = True
            return RecommendationResponse(**cached_data)
        
        # 오프셋 계산
        offset = (page - 1) * limit
        
        logger.info(f"📥 추천 요청: category={category}, date={date}, page={page}, limit={limit}")
        
        # 전체 개수 조회
        count_query = """
            SELECT COUNT(DISTINCT r.books_isbn)
            FROM tb_recommend r
            JOIN tb_news_keyword n ON r.news_id = n.news_id
            JOIN tb_books b ON r.books_isbn = b.books_isbn
            WHERE n.news_category = %s
        """
        count_params = [category]
        
        if date:
            count_query += " AND DATE(n.news_date) = %s"
            count_params.append(date)
        
        try:
            total_result = db.fetch_query(count_query, count_params)
            total = total_result[0][0] if total_result else 0
        except Exception as e:
            logger.error(f"❌ 전체 개수 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="데이터베이스 조회 중 오류가 발생했습니다.")
        
        if total == 0:
            raise HTTPException(
                status_code=404,
                detail=f"'{category}' 카테고리에 대한 추천 도서를 찾을 수 없습니다."
            )
        
        # 데이터 조회
        data_query = """
            SELECT DISTINCT
                b.books_isbn, n.news_category, b.books_img,
                b.books_description, b.books_title, b.books_publisher,
                n.news_date, r.similarity_score
            FROM tb_recommend r
            JOIN tb_news_keyword n ON r.news_id = n.news_id
            JOIN tb_books b ON r.books_isbn = b.books_isbn
            WHERE n.news_category = %s
        """
        data_params = [category]
        
        if date:
            data_query += " AND DATE(n.news_date) = %s"
            data_params.append(date)
        
        data_query += " ORDER BY r.similarity_score DESC, n.news_date DESC LIMIT %s OFFSET %s"
        data_params.extend([limit, offset])
        
        try:
            rows = db.fetch_query(data_query, data_params)
        except Exception as e:
            logger.error(f"❌ 데이터 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="데이터베이스 조회 중 오류가 발생했습니다.")
        
        # 응답 데이터 구성
        books = [
            BookResponse(
                books_isbn=row[0],
                news_category=row[1],
                books_img=row[2],
                books_description=row[3],
                books_title=row[4],
                books_publisher=row[5],
                similarity_score=float(row[7]) if row[7] else None
            )
            for row in rows
        ]
        
        total_pages = (total + limit - 1) // limit
        
        response_data = {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "books": books,
            "cache_hit": False
        }
        
        # 캐시 저장
        set_cached_data(cache_key, response_data)
        
        process_time = time.time() - start_time
        logger.info(f"📤 추천 응답: {len(books)}권, {process_time:.3f}초")
        
        return RecommendationResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 추천 API 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="내부 서버 오류가 발생했습니다.")

@router.get(
    "/visualize",
    summary="모델 시각화",
    description="NLP 모델의 시각화를 실행합니다.",
    responses={
        200: {"description": "시각화 완료"},
        500: {"model": ErrorResponse, "description": "시각화 실패"}
    }
)
async def visualize_model():
    """NLP 모델 시각화"""
    try:
        logger.info("📊 NLP 모델 시각화 시작")
        nlp = Nlp()
        nlp.LoadModel()
        nlp.VisualizeModel()
        logger.info("✅ NLP 모델 시각화 완료")
        return {"message": "✅ 모델 시각화 완료 (로컬에서 실행됨)"}
    except Exception as e:
        logger.error(f"❌ 모델 시각화 실패: {e}")
        raise HTTPException(status_code=500, detail="모델 시각화 중 오류가 발생했습니다.")

@router.get(
    "/categories",
    summary="사용 가능한 카테고리",
    description="사용 가능한 뉴스 카테고리 목록을 반환합니다."
)
async def get_categories():
    """사용 가능한 카테고리 목록"""
    categories = [
        {"id": "politics", "name": "정치", "description": "정치 관련 뉴스"},
        {"id": "sports", "name": "스포츠", "description": "스포츠 관련 뉴스"},
        {"id": "economic", "name": "경제", "description": "경제 관련 뉴스"},
        {"id": "society", "name": "사회", "description": "사회 관련 뉴스"},
        {"id": "world", "name": "국제", "description": "국제 관련 뉴스"}
    ]
    return {"categories": categories}

@router.get(
    "/cache/clear",
    summary="캐시 초기화",
    description="추천 시스템 캐시를 초기화합니다."
)
async def clear_cache():
    """캐시 초기화"""
    try:
        global recommendation_cache, cache_timestamps
        recommendation_cache.clear()
        cache_timestamps.clear()
        logger.info("🗑️ 캐시 초기화 완료")
        return {"message": "캐시가 성공적으로 초기화되었습니다."}
    except Exception as e:
        logger.error(f"❌ 캐시 초기화 실패: {e}")
        raise HTTPException(status_code=500, detail="캐시 초기화 중 오류가 발생했습니다.")

@router.get(
    "/cache/status",
    summary="캐시 상태",
    description="현재 캐시 상태를 확인합니다."
)
async def get_cache_status():
    """캐시 상태 확인"""
    try:
        cache_size = len(recommendation_cache)
        cache_keys = list(recommendation_cache.keys())
        return {
            "cache_size": cache_size,
            "cache_keys": cache_keys,
            "cache_ttl": CACHE_TTL
        }
    except Exception as e:
        logger.error(f"❌ 캐시 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="캐시 상태 조회 중 오류가 발생했습니다.")
