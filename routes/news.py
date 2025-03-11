from fastapi import APIRouter, HTTPException, Query
import requests
import os
from dotenv import load_dotenv

router = APIRouter()

# Load environment variables
load_dotenv()

# 네이버 API 클라이언트 ID와 시크릿 키 가져오기
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

@router.get("/api/news")
async def get_news(query: str = Query(..., description="농업 관련 키워드")):
    try:
        # 네이버 뉴스 API 엔드포인트 URL
        url = "https://openapi.naver.com/v1/search/news.json"
        
        # 요청 헤더에 클라이언트 ID와 시크릿 키 추가
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        
        # 요청 매개변수
        params = {
            "query": query,
            "display": 6,  # 한 번에 가져올 뉴스 개수
            "start": 1,     # 시작 인덱스
            "sort": "date"  # 정렬 기준 (date: 날짜순)
        }
        
        # API 요청
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
        # JSON 응답 반환
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"네이버 뉴스 API 호출 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="뉴스 데이터를 가져오는데 실패했습니다") 