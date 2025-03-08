import urllib.request
import urllib.parse
import json

class NaverApi:
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://openapi.naver.com/v1/search/book.json"
        self.start = 1
        self.querys = [
            "소설", "시/에세이", "인문", "요리", "건강",
            "취미/실용/스포츠", "경제/경영", "자기계발",
            "정치/사회", "역사/문화", "예술/대중문화",
            "기술/공학", "외국어", "과학", "여행", "컴퓨터/IT"
        ]

    def request_api(self, query, sort="sim", display=100, start=1):
        """Request data from Naver Book Search API."""
        
        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": sort
        }

        encoded_params = urllib.parse.urlencode(params)
        url = f"{self.base_url}?{encoded_params}"
        
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)

        try:
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
            
            if rescode == 200:
                response_body = response.read()
                return json.loads(response_body.decode('utf-8'))
            else:
                print(f"Error Code: {rescode}")
                return None

        except Exception as e:
            print(f"An error occurred while requesting '{query}': {e}")
            return None

    def fetch_books_by_category(self):
        """Fetch books for each category in `self.querys`."""
        all_books = {}

        for query in self.querys:
            print(f"Fetching books for category: {query}")
            result = self.request_api(query=query)

            if result and "items" in result:
                all_books[query] = result["items"]
            else:
                print(f"No data found for category: {query}")

        return all_books
    
    def KeywordExtraction(self):
        all_books = self.fetch_books_by_category()
        book_description = []
        for category, books in all_books.items():
            print(f"\n[{category}] 카테고리에서 {len(books)}권의 책을 찾았습니다.")
            for book in books[:3]:  # 각 카테고리에서 상위 3개 책만 출력
                book_description.append(book['description'])
        
        return book_description
    
        
