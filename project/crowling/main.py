import sys
import os
from collections import Counter  # ✅ 단어 빈도수 계산을 위한 라이브러리
import pandas as pd

# ✅ 현재 파일(`main.py`)의 상위 폴더를 기준으로 `nlp` 폴더의 경로를 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nlp")))

from News import News
from Nlp import Nlp  # ✅ Nlp 클래스 가져오기

if __name__ == "__main__":
    
    nlp = Nlp()
    
    api_key = ""  # API 키
    news_api = News(api_key)
    startDate = "2025-03-09"
    endDate = "2025-03-09"
    # ✅ 현대자동차(KRX:005380)의 특정 날짜 뉴스 가져오기
    news_data = news_api.get_news(startDate=startDate, endDate=endDate)

    # ✅ API 응답 데이터 출력 (디버깅 용도)
    print("📌 API 응답 데이터 구조:", news_data.keys())

    # ✅ title 값만 리스트로 저장 (`data` 키 사용)
    titles = []
    if news_data and "data" in news_data and isinstance(news_data["data"], list):  
        titles = [article["title"] for article in news_data["data"] if "title" in article]
    
    print("📌 뉴스 제목 리스트:", titles)  # ✅ 뉴스 제목 리스트 확인

    # ✅ 뉴스 제목이 있을 경우에만 KonlpyOkt 실행
    if titles:
        nouns_list = nlp.KonlpyOkt(titles)  # ✅ 명사 리스트 추출
        
        # ✅ 리스트를 평탄화하여 하나의 리스트로 변환
        all_nouns = [noun for sublist in nouns_list for noun in sublist]

        # ✅ 단어 빈도수 계산
        word_counts = Counter(all_nouns)

        # ✅ 상위 5개 단어 출력
        top_5_words = word_counts.most_common(10)
        
        news_words = []
        print("🔵 가장 많이 나온 단어 TOP 5:")
        for word, count in top_5_words:
            news_words.append(word)
            
        df = pd.DataFrame(news_words)
        # Save the DataFrame to a CSV file
        df.to_csv('project/datafile/news_data.csv', index=False, encoding="utf-8")

        print(f"CSV 파일이 성공적으로 저장되었습니다: {'../datafile/news_data'}")

    
    else:
        print("⚠️ 뉴스 제목이 없습니다. API 응답을 확인하세요.")
