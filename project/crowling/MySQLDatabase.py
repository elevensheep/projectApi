import mysql.connector
from datetime import datetime

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

    def insert_top_keywords(self, section, keywords, query):
        """상위 10개 단어와 현재 datetime을 tb_newsKeyword 테이블에 저장"""
        if not self.conn or not self.cursor:
            print("❌ 데이터베이스 연결 실패. insert_top_keywords 실행 불가.")
            return
        
        query = query
        now = datetime.now()  # 현재 datetime
        data = [(now, word) for word in keywords]

        try:
            self.cursor.executemany(query, data)
            self.conn.commit()
            print(f"✅ {section.upper()} - 상위 10개 키워드 저장 완료!")
        except mysql.connector.Error as err:
            print(f"❌ 데이터 저장 실패: {err}")

    def fetch_keywords(self,query):
        """tb_newsKeyword 테이블에서 news_date와 news_keyword를 함께 조회"""
        if not self.conn or not self.cursor:
            print("❌ 데이터베이스 연결 실패. fetch_keywords 실행 불가.")
            return []

        self.query = query
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()  # 각 row: (news_date, news_keyword)
            return result
        except mysql.connector.Error as err:
            print(f"❌ 데이터 조회 실패: {err}")
            return []

    def close(self):
        """데이터베이스 연결 종료"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✅ MySQL 연결 종료!")

