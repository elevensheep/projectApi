from MySQLDatabase import MySQLDatabase
from Nlp import Nlp
from Crowling import Crowling  # Crowling 클래스가 있는 파일을 import 해야 합니다


# 이 구문은 직접 실행될 때만 실행됩니다.
if __name__ == "__main__":
    # 크롤러 인스턴스 생성
    crawler = Crowling()
    
    # 크롤러 실행
    newsData = crawler.wordExtraction()
    
    nlp = Nlp()
    
    similar_news_data = nlp.get_similar_keywords(newsData)
    
    tokens = nlp.train_book_model_and_get_tokens()
    
    db = MySQLDatabase()
    
    # db.insert_books_keywords(isbn_tokens=tokens)
    # db.insert_top_keywords(newsData=similar_news_data)
    
    fetchBookData = db.fetch_books_keywords()
    fetchNewsData = db.fetch_today_news()
    
    mappingData = db.map_books_keywords_to_news(fetchBookData, fetchNewsData)
    
    db.insert_recommendations(mapping_data=mappingData)
    
    db.close()