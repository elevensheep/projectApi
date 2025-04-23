from MySQLDatabase import MySQLDatabase
from Nlp import Nlp
from Crowling import Crowling  
import sys

if __name__ == "__main__":
    
    sys.stdout.reconfigure(encoding='utf-8')
    # 크롤러 인스턴스 생성
    crawler = Crowling()
    db = MySQLDatabase()
    nlp = Nlp()
    # 크롤러 실행
    newsData = crawler.wordExtraction()
    
    similar_news_data = nlp.get_similar_keywords(newsData)
    
    tokens = nlp.train_book_model_and_get_tokens()
    
    db.truncateBooksKeyword()
    
    db.insert_books_keywords(isbn_tokens=tokens)
    db.insert_top_keywords(newsData=similar_news_data)
    
    
    fetchBookData = db.fetch_books_keywords()
    fetchNewsData = db.fetch_today_news()
    
    mappingData = db.map_books_keywords_to_news(fetchBookData, fetchNewsData)
    
    db.insert_recommendations(mapping_data=mappingData)
    
    db.close()
    
    nlp.LoadModel()
    nlp. VisualizeModel()