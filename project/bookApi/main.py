import os
import pandas as pd
from NaverApi import NaverApi

if __name__ == "__main__":
    # Naver API 클라이언트 ID와 클라이언트 비밀키 입력
    client_id = "i2i3NNXvdhGVpvoWNA3n"
    client_secret = "h2vJ3qku6Y"
    
    querys = [
        "소설", "시/에세이", "인문", "요리", "건강",
        "취미/실용/스포츠", "경제/경영", "자기계발",
        "정치/사회", "역사/문화", "예술/대중문화",
        "기술/공학", "외국어", "과학", "여행", "컴퓨터/IT"
    ]
    
    # NaverApi 클래스 인스턴스 생성
    api = NaverApi(client_id, client_secret)
    all_books = api.KeywordExtraction(querys=querys)

    # Convert to DataFrame
    df = pd.DataFrame(all_books)

    # Save the DataFrame to a CSV file
    df.to_csv('project/datafile/books_data.csv', index=False, encoding="utf-8")

    print(f"CSV 파일이 성공적으로 저장되었습니다: {'../datafile/books_data'}")
