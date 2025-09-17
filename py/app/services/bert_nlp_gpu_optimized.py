#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPU 최적화된 BERT NLP 서비스
- CUDA 가속
- 배치 처리 최적화
- 메모리 효율성
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

class GPUBertNLP:
    """
    GPU 최적화된 KoBERT 기반 NLP 서비스
    """
    
    def __init__(self, model_name: str = "skt/kobert-base-v1", cache_dir: str = "cache"):
        """
        GPU 최적화된 BERT NLP 서비스 초기화
        
        Args:
            model_name: 사용할 BERT 모델명
            cache_dir: 캐시 디렉토리
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        
        # GPU 설정
        self.device = self._setup_gpu()
        
        # 모델 초기화
        self.tokenizer = None
        self.model = None
        self.sentence_transformer = None
        
        # 캐시 디렉토리 생성
        os.makedirs(cache_dir, exist_ok=True)
        
        # 임베딩 캐시
        self.embedding_cache = {}
        
        logger.info(f"🚀 GPU 최적화된 BERT NLP 서비스 초기화 (Device: {self.device})")
        self._load_models()
        self._load_cache()
    
    def _setup_gpu(self) -> torch.device:
        """GPU 설정 및 최적화"""
        if torch.cuda.is_available():
            # GPU 정보 출력
            gpu_count = torch.cuda.device_count()
            current_gpu = torch.cuda.current_device()
            gpu_name = torch.cuda.get_device_name(current_gpu)
            gpu_memory = torch.cuda.get_device_properties(current_gpu).total_memory / 1024**3
            
            logger.info(f"🎮 GPU 감지됨:")
            logger.info(f"   - GPU 개수: {gpu_count}")
            logger.info(f"   - 현재 GPU: {current_gpu}")
            logger.info(f"   - GPU 이름: {gpu_name}")
            logger.info(f"   - GPU 메모리: {gpu_memory:.1f}GB")
            
            # GPU 메모리 최적화 설정
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
            
            # GPU 메모리 캐시 정리
            torch.cuda.empty_cache()
            
            device = torch.device('cuda')
            
            # GPU 메모리 사용량 출력
            allocated = torch.cuda.memory_allocated(device) / 1024**2
            cached = torch.cuda.memory_reserved(device) / 1024**2
            logger.info(f"   - 할당된 메모리: {allocated:.1f}MB")
            logger.info(f"   - 캐시된 메모리: {cached:.1f}MB")
            
        else:
            logger.warning("⚠️ GPU를 사용할 수 없습니다. CPU를 사용합니다.")
            device = torch.device('cpu')
        
        return device
    
    def _load_models(self):
        """GPU 최적화된 BERT 모델들 로드"""
        try:
            # KoBERT 토크나이저와 모델 로드
            logger.info(f"KoBERT 모델 로드 중: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            
            # GPU로 모델 이동
            self.model.to(self.device)
            self.model.eval()
            
            # GPU 최적화
            if self.device.type == 'cuda':
                # 모델 컴파일 (PyTorch 2.0+)
                if hasattr(torch, 'compile'):
                    self.model = torch.compile(self.model, mode='reduce-overhead')
                
                # Mixed Precision 설정
                self.use_amp = True
                self.scaler = torch.cuda.amp.GradScaler()
                
                logger.info("✅ GPU 최적화 적용 완료")
            else:
                self.use_amp = False
                self.scaler = None
            
            # Sentence Transformer 로드 (GPU 지원)
            logger.info("Sentence Transformer 모델 로드 중...")
            self.sentence_transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            if self.device.type == 'cuda':
                self.sentence_transformer.to(self.device)
            
            logger.info("✅ 모든 GPU 최적화된 BERT 모델 로드 완료")
            
        except Exception as e:
            logger.error(f"❌ BERT 모델 로드 실패: {e}")
            raise
    
    def get_bert_embedding_gpu(self, text: str) -> np.ndarray:
        """
        GPU 최적화된 BERT 임베딩 생성
        
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
            
            # 토크나이징
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=256,
                padding=True
            )
            
            # GPU로 이동
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # GPU 최적화된 임베딩 생성
            with torch.no_grad():
                if self.use_amp:
                    # Mixed Precision 사용
                    with torch.cuda.amp.autocast():
                        outputs = self.model(**inputs)
                        embedding = outputs.last_hidden_state[:, 0, :]
                else:
                    outputs = self.model(**inputs)
                    embedding = outputs.last_hidden_state[:, 0, :]
                
                # CPU로 이동하여 numpy 변환
                embedding = embedding.cpu().numpy()
            
            result = embedding[0]
            
            # 캐시에 저장
            self.embedding_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"GPU BERT 임베딩 생성 실패: {e}")
            return np.zeros(768)
    
    def get_embeddings_batch_gpu(self, texts: List[str], batch_size: int = 64) -> List[np.ndarray]:
        """
        GPU 배치 처리로 임베딩 생성
        
        Args:
            texts: 처리할 텍스트 리스트
            batch_size: 배치 크기 (GPU 메모리에 따라 조정)
            
        Returns:
            임베딩 리스트
        """
        embeddings = []
        
        # GPU 메모리에 따른 배치 크기 조정
        if self.device.type == 'cuda':
            gpu_memory = torch.cuda.get_device_properties(self.device).total_memory / 1024**3
            if gpu_memory < 4:  # 4GB 미만
                batch_size = min(batch_size, 16)
            elif gpu_memory < 8:  # 8GB 미만
                batch_size = min(batch_size, 32)
            else:  # 8GB 이상
                batch_size = min(batch_size, 64)
        
        logger.info(f"📦 GPU 배치 처리 시작 (배치 크기: {batch_size})")
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = []
            
            # 배치 토크나이징
            batch_inputs = self.tokenizer(
                batch_texts,
                return_tensors="pt",
                truncation=True,
                max_length=256,
                padding=True
            )
            
            # GPU로 이동
            batch_inputs = {k: v.to(self.device) for k, v in batch_inputs.items()}
            
            # 배치 임베딩 생성
            with torch.no_grad():
                if self.use_amp:
                    with torch.cuda.amp.autocast():
                        outputs = self.model(**batch_inputs)
                        batch_embedding = outputs.last_hidden_state[:, 0, :]
                else:
                    outputs = self.model(**batch_inputs)
                    batch_embedding = outputs.last_hidden_state[:, 0, :]
                
                # CPU로 이동하여 numpy 변환
                batch_embedding = batch_embedding.cpu().numpy()
            
            batch_embeddings.extend(batch_embedding)
            embeddings.extend(batch_embeddings)
            
            # GPU 메모리 정리
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
        
        return embeddings
    
    def calculate_similarities_batch_gpu(self, query_text: str, candidate_texts: List[str]) -> List[float]:
        """
        GPU 배치 유사도 계산
        
        Args:
            query_text: 쿼리 텍스트
            candidate_texts: 후보 텍스트들
            
        Returns:
            유사도 점수 리스트
        """
        # 쿼리 임베딩 생성
        query_embedding = self.get_bert_embedding_gpu(query_text)
        
        # 후보 텍스트들 임베딩 생성 (GPU 배치 처리)
        candidate_embeddings = self.get_embeddings_batch_gpu(candidate_texts)
        
        # GPU에서 유사도 계산 (대용량 데이터의 경우)
        if len(candidate_embeddings) > 1000 and self.device.type == 'cuda':
            return self._calculate_similarities_gpu(query_embedding, candidate_embeddings)
        else:
            # CPU에서 계산 (소용량 데이터)
            similarities = []
            for candidate_embedding in candidate_embeddings:
                similarity = cosine_similarity([query_embedding], [candidate_embedding])[0][0]
                similarities.append(float(similarity))
            return similarities
    
    def _calculate_similarities_gpu(self, query_embedding: np.ndarray, candidate_embeddings: List[np.ndarray]) -> List[float]:
        """GPU에서 대용량 유사도 계산"""
        try:
            # numpy 배열을 GPU 텐서로 변환
            query_tensor = torch.tensor(query_embedding, device=self.device, dtype=torch.float32)
            candidate_tensor = torch.tensor(candidate_embeddings, device=self.device, dtype=torch.float32)
            
            # 정규화
            query_norm = torch.norm(query_tensor)
            candidate_norms = torch.norm(candidate_tensor, dim=1, keepdim=True)
            
            # 코사인 유사도 계산
            similarities = torch.mm(candidate_tensor, query_tensor.unsqueeze(1)).squeeze(1)
            similarities = similarities / (candidate_norms.squeeze(1) * query_norm)
            
            # CPU로 이동하여 numpy 변환
            similarities = similarities.cpu().numpy()
            
            return similarities.tolist()
            
        except Exception as e:
            logger.error(f"GPU 유사도 계산 실패: {e}")
            # CPU로 폴백
            similarities = []
            for candidate_embedding in candidate_embeddings:
                similarity = cosine_similarity([query_embedding], [candidate_embedding])[0][0]
                similarities.append(float(similarity))
            return similarities
    
    def find_similar_texts_gpu(self, query_text: str, candidate_texts: List[str], 
                              top_k: int = 5, threshold: float = 0.3) -> List[Tuple[int, float]]:
        """
        GPU 최적화된 유사 텍스트 검색
        
        Args:
            query_text: 쿼리 텍스트
            candidate_texts: 후보 텍스트들
            top_k: 반환할 상위 개수
            threshold: 유사도 임계값
            
        Returns:
            (인덱스, 유사도 점수) 튜플 리스트
        """
        try:
            # GPU 배치 유사도 계산
            similarities = self.calculate_similarities_batch_gpu(query_text, candidate_texts)
            
            # numpy 배열로 변환하여 빠른 정렬
            similarities_array = np.array(similarities)
            indices = np.argsort(similarities_array)[::-1]  # 내림차순 정렬
            
            results = []
            for idx in indices:
                if similarities_array[idx] >= threshold and len(results) < top_k:
                    results.append((idx, similarities_array[idx]))
            
            return results
            
        except Exception as e:
            logger.error(f"GPU 유사 텍스트 검색 실패: {e}")
            return []
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
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
        cache_file = os.path.join(self.cache_dir, "gpu_bert_embedding_cache.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    self.embedding_cache = pickle.load(f)
                logger.info(f"📂 GPU BERT 임베딩 캐시 로드 완료: {len(self.embedding_cache)}개")
            except Exception as e:
                logger.error(f"캐시 로드 실패: {e}")
                self.embedding_cache = {}
    
    def save_cache(self):
        """임베딩 캐시 저장"""
        cache_file = os.path.join(self.cache_dir, "gpu_bert_embedding_cache.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self.embedding_cache, f)
            logger.info(f"💾 GPU BERT 임베딩 캐시 저장 완료: {len(self.embedding_cache)}개")
        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")
    
    def get_gpu_stats(self) -> Dict[str, any]:
        """GPU 통계 정보"""
        if self.device.type == 'cuda':
            allocated = torch.cuda.memory_allocated(self.device) / 1024**2
            cached = torch.cuda.memory_reserved(self.device) / 1024**2
            total = torch.cuda.get_device_properties(self.device).total_memory / 1024**2
            
            return {
                'device': str(self.device),
                'allocated_memory_mb': allocated,
                'cached_memory_mb': cached,
                'total_memory_mb': total,
                'memory_usage_percent': (allocated / total) * 100
            }
        else:
            return {
                'device': str(self.device),
                'allocated_memory_mb': 0,
                'cached_memory_mb': 0,
                'total_memory_mb': 0,
                'memory_usage_percent': 0
            }
    
    def clear_gpu_cache(self):
        """GPU 캐시 정리"""
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()
            logger.info("🧹 GPU 캐시 정리 완료")

def test_gpu_performance():
    """GPU 성능 테스트"""
    logger.info("🧪 GPU 최적화된 BERT NLP 성능 테스트 시작")
    
    # 테스트 데이터
    test_texts = [
        "경제 위기와 금융 정책에 대한 분석",
        "정치 개혁과 민주주의 발전",
        "스포츠 경기 결과와 선수들의 활약",
        "사회 문제와 해결 방안",
        "국제 관계와 외교 정책"
    ] * 50  # 250개 텍스트
    
    # GPU 최적화된 BERT NLP 초기화
    bert_nlp = GPUBertNLP()
    
    # GPU 통계 출력
    gpu_stats = bert_nlp.get_gpu_stats()
    logger.info(f"🎮 GPU 통계: {gpu_stats}")
    
    # 성능 테스트
    start_time = time.time()
    
    # GPU 배치 처리 테스트
    embeddings = bert_nlp.get_embeddings_batch_gpu(test_texts, batch_size=64)
    
    end_time = time.time()
    
    logger.info(f"⏱️ GPU 배치 처리 시간: {end_time - start_time:.2f}초")
    logger.info(f"📊 처리된 텍스트: {len(test_texts)}개")
    logger.info(f"🚀 처리 속도: {len(test_texts) / (end_time - start_time):.2f} 텍스트/초")
    
    # GPU 유사도 검색 테스트
    query = "경제와 금융에 관한 내용"
    start_time = time.time()
    
    similar_texts = bert_nlp.find_similar_texts_gpu(query, test_texts, top_k=5)
    
    end_time = time.time()
    
    logger.info(f"🔍 GPU 유사도 검색 시간: {end_time - start_time:.2f}초")
    logger.info(f"📋 상위 유사 텍스트:")
    for idx, score in similar_texts:
        logger.info(f"   - {test_texts[idx][:50]}... (점수: {score:.4f})")
    
    # 최종 GPU 통계
    final_gpu_stats = bert_nlp.get_gpu_stats()
    logger.info(f"💾 최종 GPU 통계: {final_gpu_stats}")
    
    # 캐시 저장
    bert_nlp.save_cache()
    
    # GPU 캐시 정리
    bert_nlp.clear_gpu_cache()
    
    logger.info("✅ GPU 성능 테스트 완료")

if __name__ == "__main__":
    test_gpu_performance()
