import urllib.request
import urllib.parse
import json
import re

class NaverApi:
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://openapi.naver.com/v1/search/book.json"
        self.start = 1

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

    def fetch_books_by_category(self, querys):
        """Fetch books for each category in `self.querys`."""
        all_books = {}

        for query in querys:
            print(f"Fetching books for category: {query}")
            result = self.request_api(query=query)

            if result and "items" in result:
                all_books[query] = result["items"]
            else:
                print(f"No data found for category: {query}")

        return all_books
    
    def KeywordExtraction(self, querys):
        all_books = self.fetch_books_by_category(querys=querys)
        book_descriptions = []  # Store multiple books' descriptions
        
        for category, books in all_books.items():
            print(f"\n[{category}] 카테고리에서 {len(books)}권의 책을 찾았습니다.")
            for book in books:
                clean_description = re.sub(r'\n', '', book['description'])  # Remove newlines
                book_descriptions.append({
                    'title': book['title'],
                    'description': clean_description
                })
        
        return book_descriptions  # Return a list of books with cleaned descriptions
            
    