import os
from konlpy.tag import Okt
from gensim.models import Word2Vec
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

class Nlp:
    
    def __init__(self):
        self.okt = Okt()  # Okt 인스턴스 생성
        self.model_path = "word2vec.model"
        self.model = None
        
        # 기존 모델이 존재하면 로드
        if os.path.exists(self.model_path):
            self.model = Word2Vec.load(self.model_path)
    
    def KonlpyOkt(self, querys):
            """문장에서 명사만 추출하여 리스트로 반환 (숫자 예외 처리)"""
            result = []
            for query in querys:
                if isinstance(query, str):  # ✅ 문자열만 처리
                    nouns = self.okt.nouns(query)
                    filtered_noun = [word for word in nouns if len(word) > 1]  # 한 글자 제거
                    result.append(filtered_noun)
                else:
                    result.append([])  # ✅ 숫자(float) 등은 빈 리스트로 처리
            return result  
    
    def CreateModel(self, querys):
        """Word2Vec 모델 학습 후 저장"""
        words = self.KonlpyOkt(querys)  # 명사 리스트의 리스트 생성
        model = Word2Vec(words, vector_size=100, window=3, min_count=1, workers=4, sg=0)
        model.save(self.model_path)
        self.model = model  # 모델 업데이트
        print("✅ Word2Vec 모델이 성공적으로 학습되었습니다.")
    
    def ModelScore(self, word1, word2):
        """두 단어 간 유사도 계산"""
        if self.model is None:
            print("⚠️ 모델이 로드되지 않았습니다. 먼저 CreateModel을 실행하세요.")
            return
        
        if word1 in self.model.wv and word2 in self.model.wv:
            similarity = self.model.wv.similarity(word1, word2)
            print(f"🟢 '{word1}'과(와) '{word2}'의 유사도: {similarity:.4f}")
        else:
            print(f"⚠️ '{word1}' 또는 '{word2}'가 모델에 없습니다.")
    
    def SimilerWord(self, word):
        """특정 단어와 가장 유사한 단어 반환"""
        if self.model is None:
            print("⚠️ 모델이 로드되지 않았습니다. 먼저 CreateModel을 실행하세요.")
            return []

        if word in self.model.wv:
            similar_words = self.model.wv.most_similar(word, topn=10)
            result = [(similar_word, score) for similar_word, score in similar_words]  # ✅ 결과 저장
            return result  # ✅ 결과 반환
        else:
            print(f"⚠️ '{word}'가 모델에 없습니다.")
            return []

    
    def VisualizeModel(self, word_list=None):
        """Word2Vec 모델의 단어 벡터를 2D로 시각화"""
        if self.model is None:
            print("⚠️ 모델이 로드되지 않았습니다. 먼저 CreateModel을 실행하세요.")
            return
        
        # 단어 목록이 없으면 모델의 단어 중 일부 선택
        if word_list is None:
            word_list = self.model.wv.index_to_key[:1000]
        
        word_vectors = [self.model.wv[word] for word in word_list if word in self.model.wv]

        # PCA로 2차원 축소
        pca = PCA(n_components=2)
        reduced_vectors = pca.fit_transform(word_vectors)
        
        plt.rcParams['font.family'] = 'Malgun Gothic'
        
        # 시각화
        plt.figure(figsize=(30, 20))
        for i, word in enumerate(word_list):
            if word in self.model.wv:  # 모델에 존재하는 단어만 시각화
                plt.scatter(reduced_vectors[i, 0], reduced_vectors[i, 1])
                plt.annotate(word, (reduced_vectors[i, 0], reduced_vectors[i, 1]))

        plt.title("Word2Vec 단어 벡터 시각화 (PCA)")
        plt.xlabel("PC1")
        plt.ylabel("PC2")
        plt.show()
