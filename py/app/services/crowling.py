import requests
from bs4 import BeautifulSoup
from services.nlp import Nlp
from collections import Counter
from services.database import PostgreSQLDatabase

class Crowling:
    
    def __init__(self):
        self.sections = {
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
        self.processor = Nlp()
    
    def scrape_h2_text(self, url):
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

    def joongang(self):
        all_nouns = {}  
        for section, urls in self.sections.items():
            all_nouns[section] = []  
            for url in urls:
                h2_texts = self.scrape_h2_text(url)
                result = self.processor.KonlpyOkt(h2_texts)
                all_nouns[section].append(result) 
        return all_nouns
    
    def get_news_titles(self):
        """뉴스 제목을 그대로 반환 (BERT 시스템용)"""
        news_titles = {}
        
        for section, urls in self.sections.items():
            news_titles[section] = []
            for url in urls:
                h2_texts = self.scrape_h2_text(url)
                # 빈 제목 제거 및 필터링
                filtered_titles = [title for title in h2_texts if title and len(title.strip()) > 5]
                news_titles[section].extend(filtered_titles)
        
        return news_titles
    
    def wordExtraction(self):
        newsData = {}

        # 각 섹션별 단어 추출
        for section, h2_texts in self.joongang().items():
            words = []
            for text in h2_texts:
                if isinstance(text, list):
                    words.extend(text)
                else:
                    words.extend(text.split())

            # 섹션별 단어 개수 집계
            word_counts = Counter(words)
            top_10_words = [word for word, _ in word_counts.most_common(10)]

            # 섹션별 top 10 키워드 저장
            newsData[section] = top_10_words

        return newsData