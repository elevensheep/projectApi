import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans, DBSCAN
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
import platform
import re
from typing import List, Dict, Tuple, Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BertNLP:
    """
    KoBERT 기반 향상된 NLP 서비스
    - 문맥 기반 임베딩
    - 단어 유사도 매칭
    - 고급 유사도 계산
    """
    
    def __init__(self, model_name: str = "skt/kobert-base-v1"):
        """
        BERT NLP 서비스 초기화
        
        Args:
            model_name: 사용할 BERT 모델명
        """
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = None
        self.model = None
        self.sentence_transformer = None
        
        logger.info(f"BERT NLP 서비스 초기화 (Device: {self.device})")
        self._load_models()
    
    def _load_models(self):
        """BERT 모델들 로드"""
        try:
            # KoBERT 토크나이저와 모델 로드
            logger.info(f"KoBERT 모델 로드 중: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # Sentence Transformer 로드 (문장 임베딩용)
            logger.info("Sentence Transformer 모델 로드 중...")
            self.sentence_transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            logger.info("✅ 모든 BERT 모델 로드 완료")
            
        except Exception as e:
            logger.error(f"❌ BERT 모델 로드 실패: {e}")
            raise
    
    def get_bert_embedding(self, text: str) -> np.ndarray:
        """
        BERT를 사용한 문맥 기반 임베딩 생성
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            문맥 기반 임베딩 벡터
        """
        if not text or not isinstance(text, str):
            return np.zeros(768)  # KoBERT 기본 차원
        
        try:
            # 텍스트 전처리
            text = self._preprocess_text(text)
            
            # 토크나이징
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # GPU로 이동
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # BERT 임베딩 생성
            with torch.no_grad():
                outputs = self.model(**inputs)
                # [CLS] 토큰의 임베딩 사용 (문장 전체 표현)
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            
            return embedding[0]
            
        except Exception as e:
            logger.error(f"BERT 임베딩 생성 실패: {e}")
            return np.zeros(768)
    
    def get_sentence_embedding(self, text: str) -> np.ndarray:
        """
        Sentence Transformer를 사용한 문장 임베딩 생성
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            문장 임베딩 벡터
        """
        if not text or not isinstance(text, str):
            return np.zeros(384)  # Sentence Transformer 기본 차원
        
        try:
            text = self._preprocess_text(text)
            embedding = self.sentence_transformer.encode(text)
            return embedding
            
        except Exception as e:
            logger.error(f"Sentence Transformer 임베딩 생성 실패: {e}")
            return np.zeros(384)
    
    def _preprocess_text(self, text: str) -> str:
        """
        텍스트 전처리
        
        Args:
            text: 전처리할 텍스트
            
        Returns:
            전처리된 텍스트
        """
        # 특수문자 제거 및 공백 정리
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def calculate_contextual_similarity(self, text1: str, text2: str) -> float:
        """
        문맥 기반 유사도 계산 (뉴스 제목과 책 설명 간)
        
        Args:
            text1: 첫 번째 텍스트 (뉴스 제목)
            text2: 두 번째 텍스트 (책 설명)
            
        Returns:
            유사도 점수 (0~1)
        """
        try:
            # BERT 임베딩 생성
            embedding1 = self.get_bert_embedding(text1)
            embedding2 = self.get_bert_embedding(text2)
            
            # 코사인 유사도 계산
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"문맥 유사도 계산 실패: {e}")
            return 0.0
    
    def find_similar_texts(self, query_text: str, candidate_texts: List[str], top_k: int = 5) -> List[Tuple[int, float]]:
        """
        쿼리 텍스트와 가장 유사한 텍스트들 찾기
        
        Args:
            query_text: 쿼리 텍스트 (뉴스 제목)
            candidate_texts: 후보 텍스트들 (책 설명들)
            top_k: 반환할 상위 개수
            
        Returns:
            (인덱스, 유사도 점수) 튜플 리스트
        """
        try:
            similarities = []
            
            for i, candidate in enumerate(candidate_texts):
                if candidate:
                    similarity = self.calculate_contextual_similarity(query_text, candidate)
                    similarities.append((i, similarity))
            
            # 유사도 순으로 정렬
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"유사 텍스트 검색 실패: {e}")
            return []
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        텍스트에서 주요 키워드 추출
        
        Args:
            text: 키워드를 추출할 텍스트
            top_k: 추출할 키워드 개수
            
        Returns:
            키워드 리스트
        """
        try:
            # 토크나이징
            tokens = self.tokenizer.tokenize(text)
            
            # 특수 토큰 제거
            keywords = [token for token in tokens if not token.startswith('[') and not token.startswith('#')]
            
            # 빈도수 기반 상위 키워드 선택
            from collections import Counter
            keyword_freq = Counter(keywords)
            
            return [keyword for keyword, freq in keyword_freq.most_common(top_k)]
            
        except Exception as e:
            logger.error(f"키워드 추출 실패: {e}")
            return []
    
    def calculate_word_similarity(self, word1: str, word2: str) -> float:
        """
        단어 간 유사도 계산
        
        Args:
            word1: 첫 번째 단어
            word2: 두 번째 단어
            
        Returns:
            유사도 점수 (0~1)
        """
        try:
            # 단어를 문장으로 변환하여 임베딩
            embedding1 = self.get_bert_embedding(word1)
            embedding2 = self.get_bert_embedding(word2)
            
            # 코사인 유사도 계산
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"단어 유사도 계산 실패: {e}")
            return 0.0
    
    def cluster_texts(self, texts: List[str], n_clusters: int = 5) -> Dict[int, List[int]]:
        """
        텍스트 클러스터링
        
        Args:
            texts: 클러스터링할 텍스트 리스트
            n_clusters: 클러스터 개수
            
        Returns:
            클러스터별 텍스트 인덱스 딕셔너리
        """
        try:
            # 텍스트 임베딩 생성
            embeddings = []
            valid_indices = []
            
            for i, text in enumerate(texts):
                if text:
                    embedding = self.get_bert_embedding(text)
                    embeddings.append(embedding)
                    valid_indices.append(i)
            
            if not embeddings:
                return {}
            
            embeddings = np.array(embeddings)
            
            # K-means 클러스터링
            kmeans = KMeans(n_clusters=min(n_clusters, len(embeddings)), random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            # 결과 정리
            clusters = defaultdict(list)
            for idx, label in zip(valid_indices, cluster_labels):
                clusters[label].append(idx)
            
            return dict(clusters)
            
        except Exception as e:
            logger.error(f"텍스트 클러스터링 실패: {e}")
            return {}
    
    def visualize_embeddings(self, texts: List[str], labels: Optional[List[str]] = None, 
                           title: str = "BERT 임베딩 시각화"):
        """
        BERT 임베딩 시각화
        
        Args:
            texts: 시각화할 텍스트들
            labels: 라벨들 (선택사항)
            title: 그래프 제목
        """
        try:
            # 임베딩 생성
            embeddings = []
            valid_texts = []
            
            for text in texts:
                if text:
                    embedding = self.get_bert_embedding(text)
                    embeddings.append(embedding)
                    valid_texts.append(text)
            
            if not embeddings:
                logger.warning("시각화할 텍스트가 없습니다.")
                return
            
            embeddings = np.array(embeddings)
            
            # t-SNE로 차원 축소
            tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(embeddings)-1))
            embeddings_2d = tsne.fit_transform(embeddings)
            
            # 시각화
            plt.figure(figsize=(12, 8))
            plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], alpha=0.7)
            
            # 라벨 추가
            if labels:
                for i, label in enumerate(labels[:len(valid_texts)]):
                    plt.annotate(label, (embeddings_2d[i, 0], embeddings_2d[i, 1]), 
                               fontsize=8, alpha=0.8)
            
            plt.title(title)
            plt.xlabel('t-SNE 1')
            plt.ylabel('t-SNE 2')
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            logger.error(f"임베딩 시각화 실패: {e}")
    
    def get_text_features(self, text: str) -> Dict[str, any]:
        """
        텍스트의 다양한 특성 추출
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            텍스트 특성 딕셔너리
        """
        try:
            features = {
                'length': len(text),
                'word_count': len(text.split()),
                'embedding': self.get_bert_embedding(text),
                'keywords': self.extract_keywords(text, top_k=5)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"텍스트 특성 추출 실패: {e}")
            return {
                'length': 0,
                'word_count': 0,
                'embedding': np.zeros(768),
                'keywords': []
            }
    
    def batch_process(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        배치 처리로 임베딩 생성
        
        Args:
            texts: 처리할 텍스트 리스트
            batch_size: 배치 크기
            
        Returns:
            임베딩 리스트
        """
        try:
            embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                batch_embeddings = []
                
                for text in batch_texts:
                    if text:
                        embedding = self.get_bert_embedding(text)
                        batch_embeddings.append(embedding)
                    else:
                        batch_embeddings.append(np.zeros(768))
                
                embeddings.extend(batch_embeddings)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"배치 처리 실패: {e}")
            return [np.zeros(768)] * len(texts) 