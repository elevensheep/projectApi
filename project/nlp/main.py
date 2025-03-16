import os
import sys
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../crowling")))

try:
    from Nlp import Nlp  
    from MySQLDatabase import MySQLDatabase 
except ModuleNotFoundError as e:
    print(f"❌ 모듈을 찾을 수 없습니다: {e}")
    sys.exit(1)  # 프로그램 종료   

def train_book_model_and_get_tokens(nlp, db):
    """
    책 데이터를 이용하여 모델을 학습하고, 각 책의 description에서 KonlpyOkt 함수를 통해 
    단어 리스트를 추출하여 ISBN별로 매핑한 딕셔너리를 반환합니다.
    
    반환값: {isbn: tokens_list}
    """
    query = "SELECT books_isbn, books_description FROM tb_books"
    fetched_data_book = db.fetch_keywords(query=query)
    df_book = pd.DataFrame(fetched_data_book, columns=["books_isbn", "books_description"])
    print(df_book.info())
    
    # 모델 학습 (책의 description을 이용하여 Word2Vec 모델 생성)
    descriptions = df_book['books_description'].tolist()
    nlp.CreateModel(descriptions)
    
    isbn_tokens = {}
    for isbn, description in zip(df_book['books_isbn'], df_book['books_description']):
        tokens = nlp.KonlpyOkt([description])
        isbn_tokens[isbn] = tokens
    return isbn_tokens

def insert_books_keywords(db, isbn_tokens):
    """
    각 책의 ISBN과 그에 해당하는 토큰들을 tb_books_keyword 테이블에 삽입합니다.
    insert query: 
      INSERT INTO tb_books_keyword (books_keyword_keyword, books_isbn_1) VALUES (%s, %s)
    중복 제거는 고려하지 않고 모든 토큰을 삽입합니다.
    """
    insert_query = "INSERT INTO tb_books_keyword (books_keyword_keyword, books_isbn_1) VALUES (%s, %s)"
    data = []
    for isbn, tokens in isbn_tokens.items():
        for token in tokens:
            data.append((token, isbn))
    if data:
        try:
            db.cursor.executemany(insert_query, data)
            db.conn.commit()
            print("책 키워드가 tb_books_keyword 테이블에 삽입되었습니다.")
        except Exception as e:
            print(f"책 키워드 삽입 실패: {e}")
    else:
        print("삽입할 책 키워드 데이터가 없습니다.")

def fetch_books_keywords(db):
    """
    tb_books_keyword 테이블에서 모든 데이터를 조회합니다.
    반환값: DataFrame with columns [books_keyword_id, books_keyword_keyword, books_isbn_1]
    """
    query = "SELECT books_keyword_id, books_keyword_keyword, books_isbn_1 FROM tb_books_keyword"
    fetched_data = db.fetch_keywords(query=query)
    df = pd.DataFrame(fetched_data, columns=["books_keyword_id", "books_keyword_keyword", "books_isbn_1"])
    return df

def fetch_today_news(db):
    """
    오늘 날짜의 뉴스 데이터를 조회하여 DataFrame으로 반환합니다.
    """
    query = "SELECT news_id, news_keyword FROM tb_news_keyword WHERE DATE(news_date) = CURDATE();"
    fetched_data_news = db.fetch_keywords(query=query)
    df_news = pd.DataFrame(fetched_data_news, columns=["news_id", "news_keyword"])
    return df_news

def map_books_keywords_to_news(books_keywords_df, news_df):
    """
    tb_books_keyword 테이블에서 가져온 각 책 키워드와 오늘 뉴스의 news_keyword를 비교하여,
    일치하는 경우 (books_keyword_id, news_id) 튜플을 매핑 데이터로 만듭니다.
    
    반환값: [(books_keyword_id, news_id), ...]
    """
    mapping_data = []
    # 뉴스 데이터에서 각 news_keyword와 news_id 추출
    for _, news_row in news_df.iterrows():
        news_id = news_row["news_id"]
        news_keyword = news_row["news_keyword"]
        # tb_books_keyword 데이터 중 books_keyword_keyword가 news_keyword와 일치하는 행 찾기
        matches = books_keywords_df[books_keywords_df["books_keyword_keyword"] == news_keyword]
        for _, row in matches.iterrows():
            books_keyword_id = row["books_keyword_id"]
            mapping_data.append((books_keyword_id, news_id))
    return mapping_data

def insert_recommendations(db, mapping_data):
    """
    매핑된 데이터를 tb_recommend 테이블에 삽입합니다.
    최종 insert query는:
        INSERT INTO tb_recommend (books_keyword_id_1, news_id_1) VALUES (%s, %s)
    mapping_data는 (books_keyword_id, news_id) 튜플 리스트입니다.
    """
    if not mapping_data:
        print("매핑된 데이터가 없습니다.")
        return
    insert_query = "INSERT INTO tb_recommend (books_keyword_id_1, news_id_1) VALUES (%s, %s)"
    try:
        db.cursor.executemany(insert_query, mapping_data)
        db.conn.commit()
        print("추천 데이터가 성공적으로 삽입되었습니다.")
    except Exception as e:
        print(f"데이터 삽입 실패: {e}")

if __name__ == "__main__":
    nlp = Nlp()
    db = MySQLDatabase()
    
    # 1. 책 데이터로 모델 학습 및 ISBN별 단어 리스트 생성
    isbn_tokens = train_book_model_and_get_tokens(nlp, db)
    print("ISBN별 추출된 단어 리스트:")
    for isbn, tokens in isbn_tokens.items():
        print(f"{isbn}: {tokens}")
    
    # 2. tb_books_keyword 테이블에 책 키워드 삽입
    insert_books_keywords(db, isbn_tokens)
    
    # 3. tb_books_keyword 테이블에서 삽입된 키워드 조회
    books_keywords_df = fetch_books_keywords(db)
    print("tb_books_keyword 데이터:")
    print(books_keywords_df)
    
    # 4. 오늘 날짜의 뉴스 데이터 가져오기
    news_df = fetch_today_news(db)
    print("오늘 뉴스 데이터:")
    print(news_df)
    
    # 5. 책 키워드와 뉴스 키워드를 매핑하여 (books_keyword_id, news_id) 튜플 리스트 생성
    mapping_data = map_books_keywords_to_news(books_keywords_df, news_df)
    print("매핑 데이터 (books_keyword_id, 뉴스ID):", mapping_data)
    
    # 6. 매핑된 데이터를 tb_recommend 테이블에 삽입
    insert_recommendations(db, mapping_data)
    
    # 추가: 모델 시각화 (필요한 경우)
    nlp.VisualizeModel()
