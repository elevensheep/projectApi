from NaverApi import NaverApi

if __name__ == "__main__":
    # Naver API 클라이언트 ID와 클라이언트 비밀키를 입력하세요.
    client_id = "i2i3NNXvdhGVpvoWNA3n"
    client_secret = "h2vJ3qku6Y"

    # NaverApi 클래스 인스턴스 생성
    api = NaverApi(client_id, client_secret)

    # 특정 카테고리(예: "소설")에 대한 책 정보를 가져오기
    print("소설 카테고리의 책 정보를 가져오는 중...")
    novel_books = api.request_api(query="소설")
    
    if novel_books and "items" in novel_books:
        print(f"소설 카테고리에서 {len(novel_books['items'])}권의 책을 찾았습니다.")
        for book in novel_books["items"][:5]:  # 상위 5개 책만 출력
            print(f"- 제목: {book['title']}, 저자: {book['author']}")
    else:
        print("소설 카테고리의 책 정보를 찾을 수 없습니다.")

    # 모든 카테고리에 대한 책 정보 가져오기
    print("\n모든 카테고리의 책 정보를 가져오는 중...")
    all_books = api.fetch_books_by_category()

    for category, books in all_books.items():
        print(f"\n[{category}] 카테고리에서 {len(books)}권의 책을 찾았습니다.")
        for book in books[:3]:  # 각 카테고리에서 상위 3개 책만 출력
            print(f"- 제목: {book['title']}, 저자: {book['author']}")
