#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
최적화된 BERT NLP 서비스
- 배치 처리
- 캐싱
- 모델 최적화
"""

import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import platform
import re
from typing import List, Dict, Tuple, Optional
import logging
import time
import pickle
import hashlib
from concurrent.futures import ThreadPoolExecutor

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedBertNLP:
    """
    최적화된 KoBERT 기반 NLP 서비스
    """
    
    def __init__(self, model_name: str = "skt/kobert-base-v1", cache_dir: str = "cache"):
        """
        최적화된 BERT NLP 서비스 초기화
        
        Args:
            model_name: 사용할 BERT 모델명
            cache_dir: 캐시 디렉토리
        """
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = None
        self.model = None
        self.sentence_transformer = None
        self.cache_dir = cache_dir
        
        # 캐시 디렉토리 생성
        os.makedirs(cache_dir, exist_ok=True)
        
        # 임베딩 캐시
        self.embedding_cache = {}
        
        logger.info(f"🚀 최적화된 BERT NLP 서비스 초기화 (Device: {self.device})")
        self._load_models()
        self._load_cache()
    
    def _load_models(self):
        """BERT 모델들 로드 (최적화)"""
        try:
            # KoBERT 토크나이저와 모델 로드
            logger.info(f"KoBERT 모델 로드 중: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # 모델 최적화
            if hasattr(torch, 'compile'):
                self.model = torch.compile(self.model)  # PyTorch 2.0 컴파일
            
            # Sentence Transformer 로드 (더 가벼운 모델 사용)
            logger.info("Sentence Transformer 모델 로드 중...")
            self.sentence_transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            logger.info("✅ 모든 최적화된 BERT 모델 로드 완료")
            
        except Exception as e:
            logger.error(f"❌ BERT 모델 로드 실패: {e}")
            raise
    
    def get_bert_embedding_optimized(self, text: str) -> np.ndarray:
        """
        최적화된 BERT 임베딩 생성 (캐시 활용)
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            문맥 기반 임베딩 벡터
        """
        if not text or not isinstance(text, str):
            return np.zeros(768)
        
        # 캐시 키 생성
        cache_key = self._get_cache_key(text)
        
        # 캐시에서 확인
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        try:
            # 텍스트 전처리
            text = self._preprocess_text(text)
            
            # 토크나이징 (최적화)
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=256,  # 길이 제한으로 성능 향상
                padding=True
            )
            
            # GPU로 이동
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # BERT 임베딩 생성 (최적화)
            with torch.no_grad():
                outputs = self.model(**inputs)
                # [CLS] 토큰의 임베딩 사용
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            
            result = embedding[0]
            
            # 캐시에 저장
            self.embedding_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"BERT 임베딩 생성 실패: {e}")
            return np.zeros(768)
    
    def get_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        배치 처리로 임베딩 생성
        
        Args:
            texts: 처리할 텍스트 리스트
            batch_size: 배치 크기
            
        Returns:
            임베딩 리스트
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = []
            
            for text in batch_texts:
                if text:
                    embedding = self.get_bert_embedding_optimized(text)
                    batch_embeddings.append(embedding)
                else:
                    batch_embeddings.append(np.zeros(768))
            
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def calculate_similarities_batch(self, query_text: str, candidate_texts: List[str]) -> List[float]:
        """
        배치 유사도 계산
        
        Args:
            query_text: 쿼리 텍스트
            candidate_texts: 후보 텍스트들
            
        Returns:
            유사도 점수 리스트
        """
        # 쿼리 임베딩 생성
        query_embedding = self.get_bert_embedding_optimized(query_text)
        
        # 후보 텍스트들 임베딩 생성 (배치 처리)
        candidate_embeddings = self.get_embeddings_batch(candidate_texts)
        
        # 유사도 계산
        similarities = []
        for candidate_embedding in candidate_embeddings:
            similarity = cosine_similarity([query_embedding], [candidate_embedding])[0][0]
            similarities.append(float(similarity))
        
        return similarities
    
    def find_similar_texts_optimized(self, query_text: str, candidate_texts: List[str], 
                                   top_k: int = 5, threshold: float = 0.3) -> List[Tuple[int, float]]:
        """
        최적화된 유사 텍스트 검색
        
        Args:
            query_text: 쿼리 텍스트
            candidate_texts: 후보 텍스트들
            top_k: 반환할 상위 개수
            threshold: 유사도 임계값
            
        Returns:
            (인덱스, 유사도 점수) 튜플 리스트
        """
        try:
            # 배치 유사도 계산
            similarities = self.calculate_similarities_batch(query_text, candidate_texts)
            
            # numpy 배열로 변환하여 빠른 정렬
            similarities_array = np.array(similarities)
            indices = np.argsort(similarities_array)[::-1]  # 내림차순 정렬
            
            results = []
            for idx in indices:
                if similarities_array[idx] >= threshold and len(results) < top_k:
                    results.append((idx, similarities_array[idx]))
            
            return results
            
        except Exception as e:
            logger.error(f"유사 텍스트 검색 실패: {e}")
            return []
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리 (최적화)"""
        # 특수문자 제거 및 공백 정리
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 길이 제한
        if len(text) > 500:
            text = text[:500]
        
        return text
    
    def _get_cache_key(self, text: str) -> str:
        """캐시 키 생성"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _load_cache(self):
        """임베딩 캐시 로드"""
        cache_file = os.path.join(self.cache_dir, "bert_embedding_cache.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    self.embedding_cache = pickle.load(f)
                logger.info(f"📂 BERT 임베딩 캐시 로드 완료: {len(self.embedding_cache)}개")
            except Exception as e:
                logger.error(f"캐시 로드 실패: {e}")
                self.embedding_cache = {}
    
    def save_cache(self):
        """임베딩 캐시 저장"""
        cache_file = os.path.join(self.cache_dir, "bert_embedding_cache.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self.embedding_cache, f)
            logger.info(f"💾 BERT 임베딩 캐시 저장 완료: {len(self.embedding_cache)}개")
        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")
    
    def clear_cache(self):
        """캐시 초기화"""
        self.embedding_cache.clear()
        cache_file = os.path.join(self.cache_dir, "bert_embedding_cache.pkl")
        if os.path.exists(cache_file):
            os.remove(cache_file)
        logger.info("🗑️ BERT 캐시 초기화 완료")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """캐시 통계"""
        return {
            'cache_size': len(self.embedding_cache),
            'cache_file_size': os.path.getsize(os.path.join(self.cache_dir, "bert_embedding_cache.pkl")) if os.path.exists(os.path.join(self.cache_dir, "bert_embedding_cache.pkl")) else 0
        }

def test_performance():
    """성능 테스트"""
    logger.info("🧪 최적화된 BERT NLP 성능 테스트 시작")
    
    # 테스트 데이터
    test_texts = [
        "경제 위기와 금융 정책에 대한 분석",
        "정치 개혁과 민주주의 발전",
        "스포츠 경기 결과와 선수들의 활약",
        "사회 문제와 해결 방안",
        "국제 관계와 외교 정책"
    ] * 20  # 100개 텍스트
    
    # 최적화된 BERT NLP 초기화
    bert_nlp = OptimizedBertNLP()
    
    # 성능 테스트
    start_time = time.time()
    
    # 배치 처리 테스트
    embeddings = bert_nlp.get_embeddings_batch(test_texts, batch_size=32)
    
    end_time = time.time()
    
    logger.info(f"⏱️ 배치 처리 시간: {end_time - start_time:.2f}초")
    logger.info(f"📊 처리된 텍스트: {len(test_texts)}개")
    logger.info(f"🚀 처리 속도: {len(test_texts) / (end_time - start_time):.2f} 텍스트/초")
    
    # 유사도 검색 테스트
    query = "경제와 금융에 관한 내용"
    start_time = time.time()
    
    similar_texts = bert_nlp.find_similar_texts_optimized(query, test_texts, top_k=5)
    
    end_time = time.time()
    
    logger.info(f"🔍 유사도 검색 시간: {end_time - start_time:.2f}초")
    logger.info(f"📋 상위 유사 텍스트:")
    for idx, score in similar_texts:
        logger.info(f"   - {test_texts[idx][:50]}... (점수: {score:.4f})")
    
    # 캐시 통계
    cache_stats = bert_nlp.get_cache_stats()
    logger.info(f"💾 캐시 통계: {cache_stats}")
    
    # 캐시 저장
    bert_nlp.save_cache()
    
    logger.info("✅ 성능 테스트 완료")

if __name__ == "__main__":
    test_performance()
