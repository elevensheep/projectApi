import sys
import os
import requests
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime

# 현재 파일 위치를 기준으로 nlp 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nlp")))

# 사용자 정의 모듈 임포트
try:
    from Nlp import Nlp  
    from MySQLDatabase import MySQLDatabase 
except ModuleNotFoundError as e:
    print(f"❌ 모듈을 찾을 수 없습니다: {e}")
    sys.exit(1)  # 프로그램 종료

def scrape_h2_text(url):
    """URL에서 <h2> 태그의 텍스트를 스크래핑"""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ {url} 에서 데이터를 가져오는 중 오류 발생: {e}")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    h2_tags = soup.find_all('h2')
    return [tag.get_text(strip=True) for tag in h2_tags]

if __name__ == "__main__":
    sections = {
        "politics": [
            "https://www.joongang.co.kr/politics",
            "https://www.joongang.co.kr/politics?page=2",
            "https://www.joongang.co.kr/politics?page=3"
        ],
        "sports": [
            "https://www.joongang.co.kr/sports",
            "https://www.joongang.co.kr/sports?page=2",
            "https://www.joongang.co.kr/sports?page=3"
        ],
        "economic": [
            "https://www.joongang.co.kr/money",
            "https://www.joongang.co.kr/money?page=2",
            "https://www.joongang.co.kr/money?page=3"
        ],
        "society": [
            "https://www.joongang.co.kr/society",
            "https://www.joongang.co.kr/society?page=2",
            "https://www.joongang.co.kr/society?page=3"
        ],
        "world": [
            "https://www.joongang.co.kr/world",
            "https://www.joongang.co.kr/world?page=2",
            "https://www.joongang.co.kr/world?page=3"
        ],

    }

    processor = Nlp()
    db = MySQLDatabase()

    for section, urls in sections.items():
        all_nouns = []
        for url in urls:
            h2_texts = scrape_h2_text(url)
            result = processor.KonlpyOkt(h2_texts)
            all_nouns.extend(result)

        # 상위 10개 단어 추출
        word_counts = Counter(all_nouns)
        top_10_words = [word for word, _ in word_counts.most_common(10)]

        # 상위 10개 키워드를 DB에 저장 (현재 datetime 포함)
        db.insert_top_keywords(section, top_10_words)

        print(f"\n🟢 스크래핑한 전체 단어 리스트 ({section.upper()}):")
        print(all_nouns)
        print(f"\n🔵 가장 많이 나온 단어 TOP 10 ({section.upper()}):")
        for word in top_10_words:
            print(word)

    # DB에 저장된 키워드와 날짜 조회
    fetched_data = db.fetch_keywords()
    print("\n📌 DB에서 가져온 키워드 및 날짜:")
    for news_date, keyword in fetched_data:
        print(f"{news_date} - {keyword}")

    db.close()

