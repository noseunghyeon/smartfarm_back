from fastapi import APIRouter, HTTPException
from . import crawler  # 상대 import 사용

router = APIRouter()

@router.get("/news-links", tags=["Crawler"])
async def get_news_links():
    """
    뉴스 관련 링크를 크롤링하여 반환합니다.
    각 뉴스 기사에 대해 이미지 URL과 내용도 함께 추가합니다.
    Postman에서 GET 요청 (예: http://localhost:8000/api/crawler/news-links)으로 테스트할 수 있습니다.
    """
    try:
        news_links = crawler.scrape_news_links()
        # 각 뉴스 기사에 대해 이미지 URL과 기사 내용 추가 (추가 HTTP 요청 발생)
        for item in news_links:
            image_url = crawler.scrape_news_image(item["link"])
            # 새로운 함수로 기사 내용을 가져옵니다.
            content = crawler.scrape_news_content(item["link"])
            item["image"] = image_url
            item["content"] = content
        return {"news_links": news_links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
    