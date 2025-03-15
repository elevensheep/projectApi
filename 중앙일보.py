import requests
from bs4 import BeautifulSoup
from konlpy.tag import Okt
import mysql.connector
from collections import Counter
from datetime import datetime

# MySQL 연결 설정 (본인 환경에 맞게 수정)
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "1111",  # 올바른 비밀번호 입력
    "database": "book"
}

class MySQLDatabase:
    def __init__(self):
        """MySQL 데이터베이스 연결"""
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

    def insert_top_keywords(self, section, keywords):
        """상위 10개 단어와 현재 datetime을 tb_newsKeyword 테이블에 저장"""
        query = "INSERT INTO tb_newsKeyword (news_date, news_keyword) VALUES (%s, %s)"
        now = datetime.now()  # 현재 datetime
        data = [(now, word) for word in keywords]
        self.cursor.executemany(query, data)
        self.conn.commit()
        print(f"✅ {section.upper()} - 상위 10개 키워드 저장 완료!")

    def fetch_keywords(self):
        """tb_newsKeyword 테이블에서 news_date와 news_keyword를 함께 조회"""
        query = "SELECT news_date, news_keyword FROM tb_newsKeyword"
        self.cursor.execute(query)
        result = self.cursor.fetchall()  # 각 row: (news_date, news_keyword)
        return result

    def close(self):
        """데이터베이스 연결 종료"""
        self.cursor.close()
        self.conn.close()

class TextProcessor:
    def __init__(self):
        """Okt 형태소 분석기 객체 생성"""
        self.okt = Okt()

    def KonlpyOkt(self, querys):
        """문장에서 명사만 추출하여 하나의 리스트로 반환 (한 글자 단어 제거)"""
        result = []
        for query in querys:
            if isinstance(query, str):
                nouns = self.okt.nouns(query)
                filtered_noun = [word for word in nouns if len(word) > 1]
                if filtered_noun:
                    result.extend(filtered_noun)
        return result

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

    processor = TextProcessor()
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
