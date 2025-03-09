from Nlp import Nlp
import pandas as pd

if __name__ == "__main__":
    nlp = Nlp()
    
    df = pd.read_csv("project/datafile/books_data.csv", encoding="utf-8-sig")
    querys = df['description'].tolist()
    
    # 모델 학습
    nlp.CreateModel(querys)

    # 단어 유사도 테스트
    nlp.ModelScore("경제", "정치")  # 두 단어의 유사도 출력
    
    # 유사한 단어 찾기
    nlp.SimilerWord("경제")

    # 단어 벡터 시각화
    nlp.VisualizeModel()
