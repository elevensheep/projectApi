import mysql.connector
from datetime import datetime
import pandas as pd
from collections import defaultdict

class MySQLDatabase:
    def __init__(self):
        """MySQL 데이터베이스 연결"""
        self.DB_CONFIG = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "1234",  # ✅ 정확한 비밀번호 입력
            "database": "book_db",
            "auth_plugin": "mysql_native_password"  # ✅ 인증 방식 명시
        }

        try:
            self.conn = mysql.connector.connect(**self.DB_CONFIG)
            self.cursor = self.conn.cursor()
            print("✅ MySQL 연결 성공!")
        except mysql.connector.Error as err:
            print(f"❌ MySQL 연결 실패: {err}")
            self.conn = None  # 연결 실패 시 None 설정
            self.cursor = None

    def insert_top_keywords(self, newsData):
        """newsData를 받아서 상위 10개 키워드를 tb_news_keyword 테이블에 저장"""
        if not self.conn or not self.cursor:
            print("❌ 데이터베이스 연결 실패. insert_top_keywords 실행 불가.")
            return

        query = """
            INSERT INTO tb_news_keyword (news_date, news_keyword, news_category) 
            VALUES (%s, %s, %s)
        """
        now = datetime.now()

        # newsData에서 (날짜, 키워드, 카테고리) 튜플 리스트 생성
        data = []
        for section, keywords in newsData.items():
            for keyword in keywords:
                data.append((now, keyword, section))

        try:
            self.cursor.executemany(query, data)
            self.conn.commit()
            print("✅ 상위 10개 키워드 저장 완료!")
        except mysql.connector.Error as err:
            self.conn.rollback()
            print(f"❌ 데이터 저장 실패: {err}")
    
    def fetch_query(self, query):
        
        if not self.conn or not self.cursor:
            print("❌ 데이터베이스 연결 실패. fetch_query 실행 불가.")
            return []

        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(f"❌ 데이터 조회 실패: {err}")
            return []
        
    def execute_query(self, query):
        if not self.conn or not self.cursor:
            print("❌ 데이터베이스 연결 실패. execute_query 실행 불가.")
            return False

        try:
            self.cursor.execute(query)
            self.conn.commit()  # 변경 사항 적용
            print("✅ 쿼리 실행 성공")
            return True
        except mysql.connector.Error as err:
            print(f"❌ 쿼리 실행 실패: {err}")
            return False
        
    def insert_books_keywords(self, isbn_tokens):
        """
        각 책의 ISBN과 그에 해당하는 토큰들을 tb_books_keyword 테이블에 삽입합니다.
        insert query: 
        INSERT INTO tb_books_keyword (books_keyword_keyword, books_isbn) VALUES (%s, %s)
        중복 제거는 고려하지 않고 모든 토큰을 삽입합니다.
        """
        insert_query = "INSERT INTO tb_books_keyword (books_keyword_keyword, books_isbn) VALUES (%s, %s)"
        data = []
        for isbn, tokens in isbn_tokens.items():
            for token in tokens:
                data.append((token, isbn))
        if data:
            try:
                self.cursor.executemany(insert_query, data)
                self.conn.commit()
                print("책 키워드가 tb_books_keyword 테이블에 삽입되었습니다.")
            except Exception as e:
                print(f"책 키워드 삽입 실패: {e}")
        else:
            print("삽입할 책 키워드 데이터가 없습니다.")
            
    def fetch_books_keywords(self):
        """
        tb_books_keyword 테이블에서 모든 데이터를 조회합니다.
        반환값: DataFrame with columns [books_keyword_id, books_keyword_keyword, books_isbn]
        """
        query = "SELECT books_keyword_id, books_keyword_keyword, books_isbn FROM tb_books_keyword"
        fetched_data = self.fetch_query(query=query)
        df = pd.DataFrame(fetched_data, columns=["books_keyword_id", "books_keyword_keyword", "books_isbn"])
        return df
    
    def fetch_today_news(self):
        """
        오늘 날짜의 뉴스 데이터를 조회하여 DataFrame으로 반환합니다.
        """
        query = "SELECT news_id, news_keyword, news_category FROM tb_news_keyword WHERE DATE(news_date) = CURDATE();"
        fetched_data_news = self.fetch_query(query=query)
        df_news = pd.DataFrame(fetched_data_news, columns=["news_id", "news_keyword", "news_category"])
        
        return df_news
    
    def map_books_keywords_to_news(self, books_df, news_df):
        """
        책 키워드 데이터와 뉴스 키워드 데이터를 비교하여 book_isbn과 news_id를 매핑하며,
        각 뉴스 카테고리별로 최대 5개씩만 저장.

        매개변수:
            books_df (pd.DataFrame): [books_keyword_id, books_keyword_keyword, books_isbn]
            news_df (pd.DataFrame): [news_id, news_keyword, news_category]

        반환값:
            list of tuples: [(books_isbn, news_id), ...]
        """
        mapping_data = defaultdict(list)
        
        # 뉴스 데이터에서 각 news_keyword, news_id, news_category 추출
        for _, news_row in news_df.iterrows():
            news_id = news_row["news_id"]
            news_keyword = news_row["news_keyword"]
            news_category = news_row["news_category"]
            
            # 책 데이터 중 books_keyword_keyword가 news_keyword와 일치하는 행 찾기
            matches = books_df[books_df["books_keyword_keyword"] == news_keyword]
            
            for _, row in matches.iterrows():
                book_isbn = row["books_isbn"]
                
                # 해당 카테고리에 대해 5개 이상이면 추가하지 않음
                if len(mapping_data[news_category]) < 5:
                    mapping_data[news_category].append((book_isbn, news_id))
        
        # 딕셔너리 값을 리스트로 변환
        result = [item for sublist in mapping_data.values() for item in sublist]
        
        return result

    def truncateBooksKeyword(self):
        query = "TRUNCATE TABLE tb_books_keyword"
        self.execute_query(query)
        
    def insert_recommendations(self, mapping_data):
        """
        매핑된 데이터를 tb_recommend 테이블에 삽입합니다.
        최종 insert query는:
            INSERT INTO tb_recommend (books_keyword_id_1, news_id_1) VALUES (%s, %s)
        mapping_data는 (books_keyword_id, news_id) 튜플 리스트입니다.
        """
        if not mapping_data:
            print("매핑된 데이터가 없습니다.")
            return
        insert_query = "INSERT INTO tb_recommend (books_isbn, news_id) VALUES (%s, %s)"
        try:
            self.cursor.executemany(insert_query, mapping_data)
            self.conn.commit()
            print("추천 데이터가 성공적으로 삽입되었습니다.")
        except Exception as e:
            print(f"데이터 삽입 실패: {e}")
            
    def close(self):
        """데이터베이스 연결 종료"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✅ MySQL 연결 종료!")