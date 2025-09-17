#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
애플리케이션 설정 관리
"""

import os
from typing import List
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    """애플리케이션 설정 클래스"""
    
    # 기본 애플리케이션 설정
    APP_NAME: str = os.getenv("APP_NAME", "News-Book Recommender API")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # 데이터베이스 설정
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "bookdb")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_AUTH_PLUGIN: str = os.getenv("DB_AUTH_PLUGIN", "mysql_native_password")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    
    # 추천 시스템 설정
    ENABLE_BERT: bool = os.getenv("ENABLE_BERT", "True").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1시간
    
    # CORS 설정
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    
    # 서버 설정
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # 성능 설정
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    RELOAD: bool = os.getenv("RELOAD", "False").lower() == "true"
    
    @classmethod
    def get_database_url(cls) -> str:
        """데이터베이스 URL 생성"""
        return f"mysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def get_database_config(cls) -> dict:
        """데이터베이스 설정 딕셔너리 반환"""
        return {
            "host": cls.DB_HOST,
            "port": cls.DB_PORT,
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD,
            "database": cls.DB_NAME,
            "auth_plugin": cls.DB_AUTH_PLUGIN,
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
            "autocommit": False,
            "pool_name": "bookdb_pool",
            "pool_size": cls.DB_POOL_SIZE,
            "pool_reset_session": True
        }

# 전역 설정 인스턴스
settings = Settings() 