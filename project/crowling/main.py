import sys
import os
from collections import Counter  
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nlp")))

from News import News
from Nlp import Nlp  

if __name__ == "__main__":
    nlp = Nlp()
    
    api_key = "af3ef99cf803400c837a27538088ada1"  
    news_api = News(api_key)
    
    # 현재 날짜를 YYYY-MM-DD 형식으로 가져오기
    today = datetime.today().strftime("%Y-%m-%d")
    startDate = today
    endDate = today

    news_data = news_api.get_news(startDate=startDate, endDate=endDate)

    print("📌 API 응답 데이터 구조:", news_data.keys())

    titles = []
    if news_data and "data" in news_data and isinstance(news_data["data"], list):  
        titles = [article["title"] for article in news_data["data"] if "title" in article]
    
    print("📌 뉴스 제목 리스트:", titles)  

    if titles:
        nouns_list = nlp.KonlpyOkt(titles)  
        
        all_nouns = [noun for sublist in nouns_list for noun in sublist]

        word_counts = Counter(all_nouns)

        top_10_words = word_counts.most_common(10)
        
        news_words = []
        print("🔵 가장 많이 나온 단어 TOP 10:")
        for word, count in top_10_words:
            news_words.append(word)
        
        # DataFrame 생성 (컬럼 추가)
        df = pd.DataFrame(news_words, columns=["word"])
        
        # Save the DataFrame to a CSV file
        csv_path = "project/datafile/news_data.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8")

        print(f"✅ CSV 파일이 성공적으로 저장되었습니다: {csv_path}")

    else:
        print("⚠️ 뉴스 제목이 없습니다. API 응답을 확인하세요.")
