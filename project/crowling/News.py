import requests

class News:
    def __init__(self, apiKey):
        self.base_url = "https://api-v2.deepsearch.com/v1/articles?"
        self.apiKey = apiKey  
    
    def get_news(self, startDate, endDate, page = 1, page_size = 100):
        """주어진 날짜 범위와 심볼로 뉴스 데이터를 요청"""
        params = {
            "date_from": startDate,
            "date_to": endDate,
            "api_key": self.apiKey,
            "page" : page,
            "page_size" : page_size
        }

        response = requests.get(self.base_url, params=params)

        if response.status_code == 200:
            return response.json() 
        else:
            print(f"⚠️ 오류 발생! 상태 코드: {response.status_code}")
            return None  
        
    