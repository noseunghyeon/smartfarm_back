from fastapi import APIRouter, HTTPException, Query
from . import crawler  # 상대 import 사용

router = APIRouter()

@router.get("/news-links", tags=["Crawler"])
async def get_news_links(               
    list_id: int = Query(19, alias="list"),
    pages: int = Query(1)  # 추가: 스크랩할 페이지 수 (기본값 1)
):
    """
    뉴스 관련 링크를 크롤링하여 반환합니다.
    각 뉴스 기사에 대해 이미지 URL과 내용도 함께 추가합니다.
    Query parameter 'list'를 통해 크롤링할 URL 번호를 지정하며,
    'pages' 파라미터로 추가 페이지 수를 지정할 수 있습니다.
      - /news-links?list=19 : 첫 페이지 (SaleNews 기본값)
      - /news-links?list=19&pages=3 : 1~3 페이지의 뉴스 기사 스크랩
    """
    try:
        # list_id를 통해 크롤링 대상 URL 생성
        url = f"https://www.nongmin.com/list/{list_id}"
        news_links = crawler.scrape_news_links(url, pages)
        # 각 뉴스 기사에 대해 이미지 URL과 기사 내용 추가 (추가 HTTP 요청 발생)
        for item in news_links:
            image_url = crawler.scrape_news_image(item["link"])
            content = crawler.scrape_news_content(item["link"])
            item["image"] = image_url
            item["content"] = content
        return {"news_links": news_links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
    