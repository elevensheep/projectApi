import mysql.connector
from datetime import datetime
import pandas as pd
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv()  # 🔑 .env 파일 로드

class MySQLDatabase:
    def __init__(self):
        """MySQL 데이터베이스 연결"""
        self.DB_CONFIG = {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT")),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
            "auth_plugin": os.getenv("DB_AUTH_PLUGIN", "mysql_native_password")
        }

        try:
            self.conn = mysql.connector.connect(**self.DB_CONFIG)
            self.cursor = self.conn.cursor()
            print("✅ MySQL 연결 성공!")
        except mysql.connector.Error as err:
            print(f"❌ MySQL 연결 실패: {err}")
            self.conn = None  # 연결 실패 시 None 설정
            self.cursor = None

    def ensure_connection(self):
        """연결이 끊겼을 경우 재연결"""
        if self.conn is None or not self.conn.is_connected():
            try:
                self.conn = mysql.connector.connect(**self.DB_CONFIG)
                self.cursor = self.conn.cursor()
                print("🔄 MySQL 재연결 성공!")
            except mysql.connector.Error as err:
                print(f"❌ MySQL 재연결 실패: {err}")
                self.conn = None
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
    
    def fetch_query(self, query, params=None):
        self.ensure_connection()  # 💡 커넥션 살아있는지 확인

        if not self.conn or not self.cursor:
            print("❌ 데이터베이스 연결 실패. fetch_query 실행 불가.")
            return []

        try:
            self.cursor.execute(query, params or [])
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(f"❌ 데이터 조회 실패: {err}")
            return []


    def execute_query(self, query, params=None):
        self.ensure_connection()
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            print("✅ 쿼리 실행 성공!")
        except Exception as e:
            print("❌ 쿼리 실행 실패:", e)
            if self.conn and self.conn.is_connected():
                self.conn.rollback()
    
        
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
        print("🔌 MySQL 연결 종료")

    def add_similarity_score_column(self):
        """tb_recommend 테이블에 similarity_score 컬럼 추가"""
        try:
            # 컬럼이 존재하는지 확인
            check_query = """
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'tb_recommend' 
                AND COLUMN_NAME = 'similarity_score'
            """
            result = self.fetch_query(check_query, (self.DB_CONFIG["database"],))
            
            if not result:
                # 컬럼이 없으면 추가
                alter_query = """
                    ALTER TABLE tb_recommend 
                    ADD COLUMN similarity_score DECIMAL(5,4) DEFAULT NULL
                """
                self.execute_query(alter_query)
                print("✅ similarity_score 컬럼이 성공적으로 추가되었습니다.")
            else:
                print("ℹ️ similarity_score 컬럼이 이미 존재합니다.")
                
        except Exception as e:
            print(f"❌ similarity_score 컬럼 추가 실패: {e}")

    def update_similarity_scores(self):
        """기존 추천 데이터에 기본 similarity_score 값 설정"""
        try:
            update_query = """
                UPDATE tb_recommend 
                SET similarity_score = 1.0 
                WHERE similarity_score IS NULL
            """
            self.execute_query(update_query)
            print("✅ 기존 추천 데이터에 기본 similarity_score가 설정되었습니다.")
            
        except Exception as e:
            print(f"❌ similarity_score 업데이트 실패: {e}")