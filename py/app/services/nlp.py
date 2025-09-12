import os
from konlpy.tag import Kkma, Okt, Komoran
from gensim.models import Word2Vec, FastText
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import pandas as pd
from app.services.database import MySQLDatabase
from sklearn.decomposition import PCA
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import platform
from matplotlib.patches import Patch
import re
from collections import Counter
import jamo
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Nlp:
    
    def __init__(self):
        # 여러 형태소 분석기 사용
        self.kkma = Kkma()
        self.okt = Okt()
        self.komoran = Komoran()
        self.model_path = "word2vec.model"
        self.fasttext_path = "fasttext.model"
        self.model = None
        self.fasttext_model = None
        self.db = MySQLDatabase()
        
        # 기존 모델이 존재하면 로드
        if os.path.exists(self.model_path):
            self.model = Word2Vec.load(self.model_path)
        if os.path.exists(self.fasttext_path):
            self.fasttext_model = FastText.load(self.fasttext_path)
    
    def preprocess_text(self, text):
        """텍스트 전처리 개선"""
        if not isinstance(text, str):
            return ""
        
        # 특수문자 제거 및 정규화
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 불용어 제거
        stopwords = {
            '이', '그', '저', '것', '수', '등', '및', '또는', '그리고', '하지만', '그러나',
            '때', '곳', '말', '일', '년', '월', '일', '시', '분', '초', '개', '명', '권',
            '쪽', '장', '회', '번', '차', '회', '번째', '첫째', '둘째', '셋째',
            '무엇', '어떤', '어떻게', '왜', '언제', '어디서', '누가', '어떤', '무슨'
        }
        
        return text
    
    def extract_nouns_enhanced(self, texts):
        """향상된 명사 추출 - 여러 형태소 분석기 조합"""
        result = []
        
        for text in texts:
            if not isinstance(text, str):
                continue
                
            text = self.preprocess_text(text)
            if not text:
                continue
            
            # 여러 형태소 분석기 사용
            nouns_kkma = set(self.kkma.nouns(text))
            nouns_okt = set(self.okt.nouns(text))
            nouns_komoran = set(self.komoran.nouns(text))
            
            # 교집합으로 신뢰도 높은 명사만 추출
            common_nouns = nouns_kkma & nouns_okt & nouns_komoran
            
            # 합집합으로 더 많은 명사 포함
            all_nouns = nouns_kkma | nouns_okt | nouns_komoran
            
            # 최종 결과: 공통 명사 + 길이가 2 이상인 단어
            filtered_nouns = []
            for noun in all_nouns:
                if len(noun) > 1 and (noun in common_nouns or len(noun) > 2):
                    filtered_nouns.append(noun)
            
            result.extend(filtered_nouns)
        
        return result
    
    def KonlpyOkt(self, querys):
        """기존 메서드 호환성을 위한 래퍼"""
        return self.extract_nouns_enhanced(querys)
    
    def CreateModel(self, querys, model_type='word2vec'):
        """향상된 모델 학습"""
        sentences = []
        
        for query in querys:
            if isinstance(query, str):
                tokens = self.extract_nouns_enhanced([query])
                if tokens:
                    sentences.append(tokens)
        
        if model_type == 'word2vec':
            # Word2Vec 하이퍼파라미터 튜닝
            model = Word2Vec(
                sentences, 
                vector_size=200,  # 벡터 크기 증가
                window=5,         # 윈도우 크기 증가
                min_count=2,      # 최소 빈도 증가
                workers=4, 
                sg=1,             # Skip-gram 사용
                negative=10,      # Negative sampling
                alpha=0.025,      # 학습률
                epochs=20         # 에포크 수 증가
            )
            model.save(self.model_path)
            self.model = model
            
        elif model_type == 'fasttext':
            # FastText 모델 (서브워드 정보 활용)
            model = FastText(
                sentences,
                vector_size=200,
                window=5,
                min_count=2,
                workers=4,
                sg=1,
                negative=10,
                alpha=0.025,
                epochs=20
            )
            model.save(self.fasttext_path)
            self.fasttext_model = model
        
        print(f"✅ {model_type.upper()} 모델이 성공적으로 학습되었습니다.")
        print(f"📊 학습된 문장 수: {len(sentences)}")
        print(f"📊 어휘 크기: {len(model.wv.key_to_index)}")
    
    def train_book_model_and_get_tokens(self):
        """향상된 책 모델 학습"""
        query = "SELECT books_isbn, books_description FROM tb_books WHERE books_description IS NOT NULL AND books_description != ''"
        fetched_data_book = self.db.fetch_query(query=query)
        df_book = pd.DataFrame(fetched_data_book, columns=["books_isbn", "books_description"])
        
        print(f"📚 총 {len(df_book)}개의 책 데이터로 모델 학습")
        
        # 모델 학습
        descriptions = df_book['books_description'].tolist()
        self.CreateModel(descriptions, 'word2vec')
        self.CreateModel(descriptions, 'fasttext')
        
        # 토큰 추출
        isbn_tokens = {}
        for isbn, description in zip(df_book['books_isbn'], df_book['books_description']):
            tokens = self.extract_nouns_enhanced([description])
            isbn_tokens[isbn] = tokens
            
        return isbn_tokens
    
    def ModelScore(self, word1, word2):
        """향상된 유사도 계산"""
        if self.model is None:
            print("⚠️ Word2Vec 모델이 로드되지 않았습니다.")
            return
        
        if self.fasttext_model is None:
            print("⚠️ FastText 모델이 로드되지 않았습니다.")
            return
        
        # Word2Vec 유사도
        if word1 in self.model.wv and word2 in self.model.wv:
            w2v_similarity = self.model.wv.similarity(word1, word2)
            print(f"🟢 Word2Vec '{word1}' ↔ '{word2}': {w2v_similarity:.4f}")
        
        # FastText 유사도
        if word1 in self.fasttext_model.wv and word2 in self.fasttext_model.wv:
            ft_similarity = self.fasttext_model.wv.similarity(word1, word2)
            print(f"🔵 FastText '{word1}' ↔ '{word2}': {ft_similarity:.4f}")
        
        # 평균 유사도
        similarities = []
        if word1 in self.model.wv and word2 in self.model.wv:
            similarities.append(w2v_similarity)
        if word1 in self.fasttext_model.wv and word2 in self.fasttext_model.wv:
            similarities.append(ft_similarity)
        
        if similarities:
            avg_similarity = np.mean(similarities)
            print(f"📊 평균 유사도: {avg_similarity:.4f}")
    
    def SimilerWord(self, word, topn=5):
        """향상된 유사 단어 찾기"""
        if self.model is None:
            print("⚠️ 모델이 로드되지 않았습니다.")
            return []

        results = []
        
        # Word2Vec 결과
        if word in self.model.wv:
            w2v_similar = self.model.wv.most_similar(word, topn=topn)
            results.extend([(word, score, 'Word2Vec') for word, score in w2v_similar])
        
        # FastText 결과
        if self.fasttext_model and word in self.fasttext_model.wv:
            ft_similar = self.fasttext_model.wv.most_similar(word, topn=topn)
            results.extend([(word, score, 'FastText') for word, score in ft_similar])
        
        # 점수로 정렬
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:topn]

    def get_similar_keywords(self, newsData):
        """향상된 키워드 유사도 매칭"""
        similar_news_data = {}

        for section, keywords in newsData.items():
            similar_keywords = []
            
            for keyword in keywords:
                similar_words = self.SimilerWord(keyword, topn=3)
                
                if similar_words:
                    # 가장 높은 점수의 단어 선택
                    best_match = similar_words[0]
                    similar_keywords.append({
                        'original': keyword,
                        'similar': best_match[0],
                        'score': best_match[1],
                        'model': best_match[2]
                    })
            
            similar_news_data[section] = similar_keywords

        return similar_news_data

    def LoadModel(self):
        """모델 로드"""
        if os.path.exists(self.model_path):
            try:
                self.model = Word2Vec.load(self.model_path)
                print("📦 Word2Vec 모델이 성공적으로 로드되었습니다.")
            except Exception as e:
                print("🚨 Word2Vec 모델 로딩 중 오류:", e)
        
        if os.path.exists(self.fasttext_path):
            try:
                self.fasttext_model = FastText.load(self.fasttext_path)
                print("📦 FastText 모델이 성공적으로 로드되었습니다.")
            except Exception as e:
                print("🚨 FastText 모델 로딩 중 오류:", e)
    
    def find_optimal_clusters_elbow(self, word_vectors, max_clusters=20):
        """엘보우 기법을 사용한 최적 클러스터 수 찾기"""
        if len(word_vectors) < 2:
            print("⚠️ 데이터가 부족합니다. 최소 2개의 데이터 포인트가 필요합니다.")
            return 2
        
        # 클러스터 수 범위 설정
        cluster_range = range(1, min(max_clusters + 1, len(word_vectors)))
        inertias = []
        silhouette_scores = []
        
        print("🔍 엘보우 기법으로 최적 클러스터 수를 찾는 중...")
        
        for n_clusters in cluster_range:
            if n_clusters == 1:
                # 클러스터가 1개일 때는 inertia 계산
                inertia = np.sum([np.sum((word_vectors - np.mean(word_vectors, axis=0))**2)])
                inertias.append(inertia)
                silhouette_scores.append(0)  # 클러스터가 1개일 때는 실루엣 점수 0
            else:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                labels = kmeans.fit_predict(word_vectors)
                inertias.append(kmeans.inertia_)
                
                if len(set(labels)) > 1:  # 최소 2개 클러스터
                    silhouette_scores.append(silhouette_score(word_vectors, labels))
                else:
                    silhouette_scores.append(0)
        
        # 엘보우 포인트 찾기 (inertia의 변화율이 급격히 감소하는 지점)
        if len(inertias) > 2:
            # 2차 미분을 사용하여 엘보우 포인트 찾기
            first_derivative = np.diff(inertias)
            second_derivative = np.diff(first_derivative)
            
            # 2차 미분이 가장 큰 지점을 엘보우 포인트로 선택
            if len(second_derivative) > 0:
                elbow_idx = np.argmax(second_derivative) + 2  # +2는 인덱스 보정
                elbow_clusters = cluster_range[elbow_idx]
            else:
                elbow_clusters = 2
        else:
            elbow_clusters = 2
        
        # 실루엣 점수 기반 최적 클러스터 수
        if len(silhouette_scores) > 1:
            silhouette_optimal = cluster_range[np.argmax(silhouette_scores[1:]) + 1]
        else:
            silhouette_optimal = 2
        
        print(f"📊 엘보우 기법 결과: {elbow_clusters}개 클러스터")
        print(f"📊 실루엣 점수 기반: {silhouette_optimal}개 클러스터")
        print(f"📊 최고 실루엣 점수: {max(silhouette_scores):.4f}")
        
        # 엘보우와 실루엣 점수를 종합하여 최적 클러스터 수 결정
        optimal_clusters = min(elbow_clusters, silhouette_optimal)
        
        return optimal_clusters, inertias, silhouette_scores, cluster_range
    
    def plot_elbow_method(self, word_vectors, max_clusters=20, save_path=None):
        """엘보우 기법 시각화"""
        if len(word_vectors) < 2:
            print("⚠️ 데이터가 부족합니다. 최소 2개의 데이터 포인트가 필요합니다.")
            return
        
        # 엘보우 기법으로 최적 클러스터 수 찾기
        optimal_clusters, inertias, silhouette_scores, cluster_range = self.find_optimal_clusters_elbow(word_vectors, max_clusters)
        
        # 그래프 설정
        if platform.system() == "Windows":
            plt.rcParams['font.family'] = 'Malgun Gothic'
        else:
            plt.rcParams['font.family'] = 'Nanum Gothic'
        
        # 서브플롯 생성
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 엘보우 그래프 (Inertia)
        ax1.plot(cluster_range, inertias, 'bo-', linewidth=2, markersize=8)
        ax1.axvline(x=optimal_clusters, color='red', linestyle='--', linewidth=2, 
                   label=f'최적 클러스터 수: {optimal_clusters}')
        ax1.set_xlabel('클러스터 수', fontsize=12)
        ax1.set_ylabel('Inertia (Within-Cluster Sum of Squares)', fontsize=12)
        ax1.set_title('엘보우 기법 (Elbow Method)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 실루엣 점수 그래프
        if len(silhouette_scores) > 1:
            ax2.plot(cluster_range[1:], silhouette_scores[1:], 'go-', linewidth=2, markersize=8)
            silhouette_optimal = cluster_range[np.argmax(silhouette_scores[1:]) + 1]
            ax2.axvline(x=silhouette_optimal, color='red', linestyle='--', linewidth=2,
                       label=f'최적 클러스터 수: {silhouette_optimal}')
            ax2.set_xlabel('클러스터 수', fontsize=12)
            ax2.set_ylabel('Silhouette Score', fontsize=12)
            ax2.set_title('실루엣 점수 (Silhouette Score)', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
        else:
            ax2.text(0.5, 0.5, '데이터 부족\n(최소 2개 클러스터 필요)', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title('실루엣 점수 (데이터 부족)', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # 그래프 저장
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 엘보우 그래프가 저장되었습니다: {save_path}")
        
        plt.show()
        
        return optimal_clusters, inertias, silhouette_scores, cluster_range
    
    def find_optimal_clusters(self, word_vectors, max_clusters=20):
        """기존 최적 클러스터 수 찾기 (호환성 유지)"""
        optimal_clusters, _, _, _ = self.find_optimal_clusters_elbow(word_vectors, max_clusters)
        return optimal_clusters
    
    def VisualizeModel(self, word_list=None, num_clusters=None, method='kmeans', use_elbow=True, show_elbow_plot=True):
        """향상된 시각화 - 엘보우 기법 통합"""
        if self.model is None:
            print("⚠️ 모델이 로드되지 않았습니다.")
            return

        # 단어 리스트 선택
        if word_list is None:
            word_list = list(self.model.wv.key_to_index)[:1000]

        # 벡터 추출
        word_list = [word for word in word_list if word in self.model.wv]
        word_vectors = np.array([self.model.wv[word] for word in word_list])

        # 차원 축소
        pca = PCA(n_components=min(50, len(word_vectors[0])))
        word_vectors_pca = pca.fit_transform(word_vectors)

        tsne = TSNE(
            n_components=2,
            perplexity=min(30, len(word_vectors) - 1),
            learning_rate=200,
            n_iter=2000,
            random_state=42,
            init='pca'
        )
        reduced_vectors = tsne.fit_transform(word_vectors_pca)

        # 클러스터링
        if num_clusters is None:
            if use_elbow:
                print("🔍 엘보우 기법을 사용하여 최적 클러스터 수를 찾는 중...")
                if show_elbow_plot:
                    # 엘보우 그래프 표시
                    optimal_clusters, inertias, silhouette_scores, cluster_range = self.plot_elbow_method(
                        reduced_vectors, max_clusters=20
                    )
                    num_clusters = optimal_clusters
                else:
                    num_clusters = self.find_optimal_clusters(reduced_vectors)
            else:
                num_clusters = self.find_optimal_clusters(reduced_vectors)
        
        if method == 'kmeans':
            clustering = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        elif method == 'dbscan':
            clustering = DBSCAN(eps=0.5, min_samples=5)
        elif method == 'agglomerative':
            clustering = AgglomerativeClustering(n_clusters=num_clusters)
        
        labels = clustering.fit_predict(reduced_vectors)
        
        # 클러스터 품질 평가
        if len(set(labels)) > 1:
            silhouette_avg = silhouette_score(reduced_vectors, labels)
            calinski_avg = calinski_harabasz_score(reduced_vectors, labels)
            print(f"📊 클러스터 품질 - 실루엣: {silhouette_avg:.4f}, 칼린스키: {calinski_avg:.4f}")

        # 시각화
        self._plot_clusters(reduced_vectors, word_list, labels, num_clusters, method)
    
    def find_clusters_with_elbow(self, word_list=None, max_clusters=20, method='kmeans'):
        """엘보우 기법을 사용한 클러스터링 전용 함수"""
        if self.model is None:
            print("⚠️ 모델이 로드되지 않았습니다.")
            return None, None, None
        
        # 단어 리스트 선택
        if word_list is None:
            word_list = list(self.model.wv.key_to_index)[:1000]
        
        # 벡터 추출
        word_list = [word for word in word_list if word in self.model.wv]
        word_vectors = np.array([self.model.wv[word] for word in word_list])
        
        # 차원 축소
        pca = PCA(n_components=min(50, len(word_vectors[0])))
        word_vectors_pca = pca.fit_transform(word_vectors)
        
        tsne = TSNE(
            n_components=2,
            perplexity=min(30, len(word_vectors) - 1),
            learning_rate=200,
            n_iter=2000,
            random_state=42,
            init='pca'
        )
        reduced_vectors = tsne.fit_transform(word_vectors_pca)
        
        # 엘보우 기법으로 최적 클러스터 수 찾기
        print("🔍 엘보우 기법을 사용하여 최적 클러스터 수를 찾는 중...")
        optimal_clusters, inertias, silhouette_scores, cluster_range = self.plot_elbow_method(
            reduced_vectors, max_clusters=max_clusters
        )
        
        # 클러스터링 실행
        if method == 'kmeans':
            clustering = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
        elif method == 'dbscan':
            clustering = DBSCAN(eps=0.5, min_samples=5)
        elif method == 'agglomerative':
            clustering = AgglomerativeClustering(n_clusters=optimal_clusters)
        
        labels = clustering.fit_predict(reduced_vectors)
        
        # 클러스터 품질 평가
        if len(set(labels)) > 1:
            silhouette_avg = silhouette_score(reduced_vectors, labels)
            calinski_avg = calinski_harabasz_score(reduced_vectors, labels)
            print(f"📊 최종 클러스터 품질 - 실루엣: {silhouette_avg:.4f}, 칼린스키: {calinski_avg:.4f}")
        
        # 클러스터별 단어 그룹화
        cluster_groups = {}
        for i, (word, label) in enumerate(zip(word_list, labels)):
            if label not in cluster_groups:
                cluster_groups[label] = []
            cluster_groups[label].append(word)
        
        print(f"✅ 총 {len(cluster_groups)}개의 클러스터가 생성되었습니다.")
        for cluster_id, words in cluster_groups.items():
            print(f"📌 클러스터 {cluster_id}: {len(words)}개 단어")
            if len(words) <= 10:  # 단어가 10개 이하면 모두 출력
                print(f"   단어들: {', '.join(words[:10])}")
            else:  # 10개 초과면 대표 단어만 출력
                print(f"   대표 단어들: {', '.join(words[:5])}... (총 {len(words)}개)")
        
        return reduced_vectors, labels, cluster_groups
    
    def _plot_clusters(self, vectors, words, labels, num_clusters, method):
        """클러스터 시각화"""
        if platform.system() == "Windows":
            plt.rcParams['font.family'] = 'Malgun Gothic'
        else:
            plt.rcParams['font.family'] = 'Nanum Gothic'

        # 색상 설정
        unique_labels = set(labels)
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))
        color_map = {label: colors[i] for i, label in enumerate(unique_labels)}
        point_colors = [color_map[label] for label in labels]

        plt.figure(figsize=(20, 15))
        scatter = plt.scatter(vectors[:, 0], vectors[:, 1], c=point_colors, alpha=0.7, s=50)

        # 단어 라벨 (중요한 단어만)
        word_freq = Counter(words)
        important_words = [word for word in words if word_freq[word] > 1]
        
        for i, word in enumerate(words):
            if word in important_words:
                plt.annotate(word, (vectors[i, 0] + 0.5, vectors[i, 1] + 0.5), 
                           fontsize=9, alpha=0.8, fontweight='bold')

        # 범례
        legend_elements = []
        for label in unique_labels:
            if label != -1:  # DBSCAN의 노이즈 클러스터 제외
                cluster_words = [words[i] for i, l in enumerate(labels) if l == label]
                if cluster_words:
                    representative_word = max(cluster_words, key=lambda w: word_freq[w])
                    legend_elements.append(
                        plt.Line2D([0], [0], marker='o', color='w', 
                                  markerfacecolor=color_map[label], 
                                  markersize=10, label=f"클러스터 {label}: {representative_word}")
                    )

        plt.legend(handles=legend_elements, title="📌 클러스터 대표 단어", 
                  loc="upper left", bbox_to_anchor=(0, 1), fontsize=10)
        
        plt.title(f"Word2Vec 단어 벡터 클러스터링 ({method.upper()})", fontsize=16)
        plt.xlabel("t-SNE-1", fontsize=12)
        plt.ylabel("t-SNE-2", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()