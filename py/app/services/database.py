#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL 데이터베이스 서비스
- 연결 풀링
- 에러 핸들링
- 로깅 시스템
- 성능 최적화
"""

import mysql.connector
from mysql.connector import pooling
from datetime import datetime
import pandas as pd
from collections import defaultdict
import os
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
from dotenv import load_dotenv

# 로깅 설정
logger = logging.getLogger(__name__)

load_dotenv()  # 🔑 .env 파일 로드

class MySQLDatabase:
    """MySQL 데이터베이스 연결 및 관리 클래스"""
    
    def __init__(self, use_pool: bool = True):
        """
        MySQL 데이터베이스 초기화
        
        Args:
            use_pool: 연결 풀 사용 여부 (기본값: True)
        """
        self.use_pool = use_pool
        self.pool = None
        self.conn = None
        self.cursor = None
        
        # 데이터베이스 설정
        self.DB_CONFIG = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "bookdb"),
            "auth_plugin": os.getenv("DB_AUTH_PLUGIN", "mysql_native_password"),
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
            "autocommit": False,
            "pool_name": "bookdb_pool",
            "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "pool_reset_session": True
        }
        
        if use_pool:
            self._initialize_pool()
        else:
            self._initialize_connection()
    
    def _initialize_pool(self):
        """연결 풀 초기화"""
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(**self.DB_CONFIG)
            logger.info("✅ MySQL 연결 풀 초기화 성공!")
        except mysql.connector.Error as err:
            logger.error(f"❌ MySQL 연결 풀 초기화 실패: {err}")
            self.pool = None
            # 폴백: 일반 연결 사용
            self._initialize_connection()
    
    def _initialize_connection(self):
        """일반 연결 초기화"""
        try:
            # 풀 설정 제거
            config = {k: v for k, v in self.DB_CONFIG.items() 
                     if not k.startswith('pool_')}
            self.conn = mysql.connector.connect(**config)
            self.cursor = self.conn.cursor()
            logger.info("✅ MySQL 연결 성공!")
        except mysql.connector.Error as err:
            logger.error(f"❌ MySQL 연결 실패: {err}")
            self.conn = None
            self.cursor = None
    
    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        if self.use_pool and self.pool:
            conn = self.pool.get_connection()
            try:
                yield conn
            finally:
                conn.close()
        else:
            if not self.conn or not self.conn.is_connected():
                self._initialize_connection()
            yield self.conn
    
    def ensure_connection(self):
        """연결 상태 확인 및 재연결"""
        if self.use_pool:
            return  # 풀 사용 시 자동 관리
        
        if self.conn is None or not self.conn.is_connected():
            try:
                self._initialize_connection()
                logger.info("🔄 MySQL 재연결 성공!")
            except mysql.connector.Error as err:
                logger.error(f"❌ MySQL 재연결 실패: {err}")
                self.conn = None
                self.cursor = None
    
    def fetch_query(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """
        쿼리 실행 및 결과 조회
        
        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            쿼리 결과 리스트
        """
        start_time = time.time()
        
        try:
            if self.use_pool and self.pool:
                with self.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query, params or ())
                        result = cursor.fetchall()
                        conn.commit()
            else:
                self.ensure_connection()
                if not self.conn or not self.cursor:
                    logger.error("❌ 데이터베이스 연결 실패")
                    return []
                
                self.cursor.execute(query, params or ())
                result = self.cursor.fetchall()
                self.conn.commit()
            
            execution_time = time.time() - start_time
            logger.debug(f"📊 쿼리 실행 완료: {execution_time:.3f}초")
            
            return result
            
        except mysql.connector.Error as err:
            logger.error(f"❌ 데이터 조회 실패: {err}")
            if self.conn and self.conn.is_connected():
                self.conn.rollback()
            return []
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {e}")
            return []
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> bool:
        """
        쿼리 실행 (INSERT, UPDATE, DELETE)
        
        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            실행 성공 여부
        """
        start_time = time.time()
        
        try:
            if self.use_pool and self.pool:
                with self.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query, params or ())
                        conn.commit()
            else:
                self.ensure_connection()
                if not self.conn or not self.cursor:
                    logger.error("❌ 데이터베이스 연결 실패")
                    return False
                
                self.cursor.execute(query, params or ())
                self.conn.commit()
            
            execution_time = time.time() - start_time
            logger.debug(f"✅ 쿼리 실행 완료: {execution_time:.3f}초")
            
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"❌ 쿼리 실행 실패: {err}")
            if self.conn and self.conn.is_connected():
                self.conn.rollback()
            return False
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {e}")
            return False
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> bool:
        """
        여러 쿼리 일괄 실행
        
        Args:
            query: SQL 쿼리
            params_list: 파라미터 리스트
            
        Returns:
            실행 성공 여부
        """
        start_time = time.time()
        
        try:
            if self.use_pool and self.pool:
                with self.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.executemany(query, params_list)
                        conn.commit()
            else:
                self.ensure_connection()
                if not self.conn or not self.cursor:
                    logger.error("❌ 데이터베이스 연결 실패")
                    return False
                
                self.cursor.executemany(query, params_list)
                self.conn.commit()
            
            execution_time = time.time() - start_time
            logger.info(f"✅ 일괄 쿼리 실행 완료: {len(params_list)}개, {execution_time:.3f}초")
            
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"❌ 일괄 쿼리 실행 실패: {err}")
            if self.conn and self.conn.is_connected():
                self.conn.rollback()
            return False
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {e}")
            return False
    
    def insert_top_keywords(self, newsData: Dict[str, List[str]]) -> bool:
        """
        뉴스 키워드를 데이터베이스에 저장
        
        Args:
            newsData: 뉴스 데이터 딕셔너리
            
        Returns:
            저장 성공 여부
        """
        query = """
            INSERT INTO tb_news_keyword (news_date, news_keyword, news_category) 
            VALUES (%s, %s, %s)
        """
        now = datetime.now()
        
        # 데이터 준비
        data = []
        for section, keywords in newsData.items():
            for keyword in keywords:
                data.append((now, keyword, section))
        
        return self.execute_many(query, data)
    
    def insert_books_keywords(self, isbn_tokens: Dict[str, List[str]]) -> bool:
        """
        책 키워드를 데이터베이스에 저장
        
        Args:
            isbn_tokens: ISBN별 키워드 딕셔너리
            
        Returns:
            저장 성공 여부
        """
        query = """
            INSERT INTO tb_books_keyword (books_isbn, books_keyword) 
            VALUES (%s, %s)
        """
        
        # 데이터 준비
        data = []
        for isbn, tokens in isbn_tokens.items():
            for token in tokens:
                data.append((isbn, token))
        
        return self.execute_many(query, data)
    
    def fetch_books_keywords(self) -> List[Tuple]:
        """책 키워드 조회"""
        query = "SELECT books_isbn, books_keyword FROM tb_books_keyword"
        return self.fetch_query(query)
    
    def fetch_today_news(self) -> List[Tuple]:
        """오늘 뉴스 조회"""
        query = """
            SELECT news_date, news_keyword, news_category 
            FROM tb_news_keyword 
            WHERE DATE(news_date) = CURDATE()
        """
        return self.fetch_query(query)
    
    def map_books_keywords_to_news(self, books_df: pd.DataFrame, news_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        책 키워드와 뉴스 키워드 매핑
        
        Args:
            books_df: 책 데이터프레임
            news_df: 뉴스 데이터프레임
            
        Returns:
            매핑 결과 리스트
        """
        mapping_data = []
        
        for _, news_row in news_df.iterrows():
            news_keyword = news_row['news_keyword']
            news_category = news_row['news_category']
            
            for _, book_row in books_df.iterrows():
                book_keywords = book_row['books_keyword'].split(',')
                
                # 키워드 매칭 확인
                if news_keyword in book_keywords:
                    mapping_data.append({
                        'news_id': news_row['news_id'],
                        'books_isbn': book_row['books_isbn'],
                        'similarity_score': 1.0  # 직접 매칭
                    })
        
        return mapping_data
    
    def truncateBooksKeyword(self) -> bool:
        """책 키워드 테이블 초기화"""
        query = "TRUNCATE TABLE tb_books_keyword"
        return self.execute_query(query)
    
    def insert_recommendations(self, mapping_data: List[Dict[str, Any]]) -> bool:
        """
        추천 결과 저장
        
        Args:
            mapping_data: 매핑 데이터 리스트
            
        Returns:
            저장 성공 여부
        """
        query = """
            INSERT INTO tb_recommend (news_id, books_isbn, similarity_score) 
            VALUES (%s, %s, %s)
        """
        
        # 데이터 준비
        data = [
            (item['news_id'], item['books_isbn'], item['similarity_score'])
            for item in mapping_data
        ]
        
        return self.execute_many(query, data)
    
    def add_similarity_score_column(self) -> bool:
        """similarity_score 컬럼 추가"""
        try:
            query = """
                ALTER TABLE tb_recommend 
                ADD COLUMN similarity_score DECIMAL(5,4) DEFAULT NULL
            """
            return self.execute_query(query)
        except mysql.connector.Error as err:
            if "Duplicate column name" in str(err):
                logger.info("ℹ️ similarity_score 컬럼이 이미 존재합니다.")
                return True
            else:
                logger.error(f"❌ similarity_score 컬럼 추가 실패: {err}")
                return False
    
    def update_similarity_scores(self) -> bool:
        """기존 similarity_score 값 업데이트"""
        query = "UPDATE tb_recommend SET similarity_score = 1.0 WHERE similarity_score IS NULL"
        return self.execute_query(query)
    
    def add_method_column(self) -> bool:
        """method 컬럼 추가"""
        try:
            query = """
                ALTER TABLE tb_recommend 
                ADD COLUMN method VARCHAR(50) DEFAULT NULL
            """
            return self.execute_query(query)
        except mysql.connector.Error as err:
            if "Duplicate column name" in str(err):
                logger.info("ℹ️ method 컬럼이 이미 존재합니다.")
                return True
            else:
                logger.error(f"❌ method 컬럼 추가 실패: {err}")
                return False
    
    def update_method_values(self) -> bool:
        """기존 method 값 업데이트"""
        query = "UPDATE tb_recommend SET method = 'traditional' WHERE method IS NULL"
        return self.execute_query(query)
    
    def get_connection_info(self) -> Dict[str, Any]:
        """연결 정보 조회"""
        return {
            "use_pool": self.use_pool,
            "pool_size": self.DB_CONFIG.get("pool_size", 0),
            "host": self.DB_CONFIG["host"],
            "port": self.DB_CONFIG["port"],
            "database": self.DB_CONFIG["database"],
            "connected": self.conn.is_connected() if self.conn else False
        }
    
    def close(self):
        """연결 종료"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn and not self.use_pool:
                self.conn.close()
            logger.info("🔚 데이터베이스 연결 종료")
        except Exception as e:
            logger.error(f"❌ 연결 종료 중 오류: {e}")
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()