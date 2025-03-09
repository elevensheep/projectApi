from Nlp import Nlp
import pandas as pd

if __name__ == "__main__":
    
    nlp = Nlp()
    # 모델 학습
    # df = pd.read_csv("project/datafile/books_data.csv", encoding="utf-8-sig")
    
    # querys = df['description'].tolist()

    # nlp.CreateModel(querys)

    # ✅ CSV 파일 읽기
    words = pd.read_csv("project/datafile/news_data.csv", encoding="utf-8-sig")

    # ✅ CSV 컬럼명 확인 후 단어 컬럼 찾기
    print("📌 CSV 파일 컬럼명:", words.columns)
    words_column_name = "단어" if "단어" in words.columns else words.columns[0]  # 자동 컬럼 탐색

    # ✅ Nlp 클래스 인스턴스 생성
    nlp = Nlp()

    # ✅ `SimilerWord` 실행 및 저장
    similer_words = [nlp.SimilerWord(x) for x in words[words_column_name]]

    # ✅ 최종 결과 출력
    print("🔵 유사한 단어 리스트:", similer_words)

    # # 단어 벡터 시각화
    # nlp.VisualizeModel()
