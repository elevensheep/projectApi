from services.crowling import Crowling
from services.database import MySQLDatabase
from datetime import datetime

def recommend_books_by_keywords(news_data: dict):
    db = MySQLDatabase()
    today = datetime.now().strftime("%Y-%m-%d")

    for category, keywords in news_data.items():
        for keyword in keywords:
            # 뉴스 키워드 저장
            insert_news_sql = """
                INSERT INTO tb_news_keyword (news_category, news_date, news_keyword)
                VALUES (%s, %s, %s)
            """
            db.execute_query(insert_news_sql, (category, today, keyword))

            # 관련 도서 검색 (책 제목 or 설명에 키워드 포함)
            book_sql = """
                SELECT books_isbn FROM tb_books 
                WHERE books_title LIKE %s OR books_description LIKE %s
            """
            matched_books = db.fetch_query(book_sql, (f'%{keyword}%', f'%{keyword}%'))

            # 도서 추천 테이블 저장
            for (isbn,) in matched_books:
                # 최신 news_id 가져오기
                news_id_sql = """
                    SELECT news_id FROM tb_news_keyword 
                    WHERE news_category = %s AND news_date = %s AND news_keyword = %s
                    ORDER BY news_id DESC LIMIT 1
                """
                news_id = db.fetch_query(news_id_sql, (category, today, keyword))[0][0]

                # 추천 저장
                insert_recommend_sql = """
                    INSERT IGNORE INTO tb_recommend (news_id, books_isbn) 
                    VALUES (%s, %s)
                """
                db.execute_query(insert_recommend_sql, (news_id, isbn))
                
    db.close()

if __name__ == "__main__":
    crawler = Crowling()
    print("📡 중앙일보 뉴스 키워드 크롤링 중...")
    news_data = crawler.wordExtraction()
    print("✅ 키워드 추출 완료:", news_data)

    print("📘 추천 도서 추출 및 저장 중...")
    recommend_books_by_keywords(news_data)
    print("✅ 추천 완료 및 DB 저장 완료")
