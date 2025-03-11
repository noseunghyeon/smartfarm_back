from fastapi import APIRouter, HTTPException, Query
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

router = APIRouter()

# Load environment variables
load_dotenv()

# 네이버 API 클라이언트 ID와 시크릿 키 가져오기
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

@router.get("/api/news")
async def get_news(query: str = Query(..., description="채소 키우는법")):
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
            "display": 3,  # 한 번에 가져올 뉴스 개수
            "start": 1,    # 시작 인덱스
            "sort": "date" # 정렬 기준 (date: 날짜순)
        }
        
        # API 요청
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
        # JSON 응답에서 뉴스 항목 추출
        news_items = response.json().get('items', [])
        
        # 각 뉴스 항목에 대해 이미지 URL 추가
        for item in news_items:
            item['imageUrl'] = await extract_image_url(item['link'])
        
        # JSON 응답 반환
        return {"items": news_items}
    
    except requests.exceptions.RequestException as e:
        print(f"네이버 뉴스 API 호출 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="뉴스 데이터를 가져오는데 실패했습니다")


async def extract_image_url(link: str):
    try:
        # 뉴스 링크에서 웹 페이지 내용 가져오기
        page_response = requests.get(link)
        page_response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(page_response.content, 'html.parser')
        
        # 1. OG 이미지 (Open Graph) 메타 태그에서 대표 이미지 URL 추출
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
        
        # 2. Twitter 카드 메타 태그에서 대표 이미지 URL 추출
        twitter_image = soup.find('meta', name='twitter:image')
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
        
        # 3. 대표 이미지를 클래스나 id로 추출 (사이트에 따라 다름)
        img_tag = soup.find('img', class_='article-image')  # 'article-image'는 예시입니다. 실제 페이지에서 확인
        if img_tag and img_tag.get('src'):
            return img_tag['src']
        
        # 4. 마지막으로 일반 이미지 태그에서 추출
        img_tag = soup.find('img', src=True)
        if img_tag and 'src' in img_tag.attrs:
            return img_tag['src']
        
        # 기본 이미지 URL 반환
        return "https://example.com/default-image.jpg"  # 기본 이미지 URL
    
    except Exception as e:
        print(f"이미지 URL 추출 중 오류 발생: {e}")
        return "https://example.com/default-image.jpg"  # 기본 이미지 URL