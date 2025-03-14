import requests # 웹 스크래핑 과정에서 http 요청을 통해 데이터를 가져오기 위한 라리브러리
from bs4 import BeautifulSoup # 뷰티풀 수프 라이브러리
from urllib.parse import urljoin

html = """
  <html>
    <body>
      <h1 id='title'>파이썬 스크래핑</h1>
      <p id='body'>웹 데이터 수집</p>
      <p class='scraping'>삼성전자 일별 시세 불러오기</p>
      <p class='scraping'>4만 전자에서 7만 전자로...</p>
    </body>
  </html>
"""

soup = BeautifulSoup(html, 'html.parser')
# print(soup)
# print(soup.stripped_strings) # 스크래핑된 문자열에서 태그를 걷어낸 문자열 저장 정보 확인

for stripped_text in soup.stripped_strings:
  print(stripped_text)

  # find() 함수를 사용하여 p 태그의 첫 번째 요소 검색
first_p = soup.find('p')
print(first_p)

# find_all() 함수를 사용하여 p 태그 전체를 검색
all_ps = soup.find_all('p')
print(all_ps)

# class 속성이 scraping인 첫 번째 요소 검색
first_scraping = soup.find(attrs={'class': 'scraping'})
print(first_scraping)

# id 속성이 body인 요소 검색
body = soup.find(attrs={'id': 'body'})
print(body)


stock_url = 'https://www.nongmin.com/economyMain'
res = requests.get(stock_url)
html = res.text # 응답에서 html 문서만 가져오기

# print(html)

# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
# text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7

# 헤더값 설정
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
}

# 헤더를 담아서 요청
res = requests.get(stock_url, headers=headers)
html = res.text

# res.text 를 뷰티풀수프에 전달하여 html.parser로 파싱
soup = BeautifulSoup(html, 'html.parser')
print(soup.find_all('tr'))

def scrape_news_links(url: str = 'https://www.nongmin.com/list/19'):
    # 헤더 설정 (봇 차단 방지를 위한 일반 브라우저 User-Agent 사용)
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/131.0.0.0 Safari/537.36'),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    # GET 요청으로 전달받은 url의 페이지 내용 가져오기
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 요청 실패 시 예외 발생
    
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    
    news_links = []
    
    # 새 뉴스 영역: <div class="news_list news_content">
    news_section = soup.find('div', class_='news_list news_content')
    if not news_section:
        return news_links
    
    # 기사 리스트는 LEFT_NEWS_LIST 영역 아래에 있는 <ul class="common_list">
    left_news_list_container = news_section.find('div', attrs={'data-layout-area': 'LEFT_NEWS_LIST'})
    if not left_news_list_container:
        return news_links
    
    common_list = left_news_list_container.find('ul', class_='common_list')
    if not common_list:
        return news_links

    # 각 <li> 항목 내의 <a> 태그에서 기사 링크 및 제목 추출
    for li in common_list.find_all('li'):
        a_tag = li.find('a', href=True)
        if not a_tag:
            continue

        link_href = a_tag['href']
        # '/article/'로 시작하는 경우에만 처리합니다.
        if not link_href.startswith('/article/'):
            continue

        # 기사의 제목은 <pre class="tit"> 태그 내부에 있음
        title_pre = a_tag.find('pre', class_='tit')
        if title_pre:
            title = title_pre.get_text(strip=True)
        else:
            title = a_tag.get_text(strip=True)

        full_link = urljoin(url, link_href)
        news_links.append({
            'title': title,
            'link': full_link
        })
        
    return news_links

def scrape_news_image(article_url):
    """
    주어진 뉴스 기사 URL을 요청하여 해당 페이지에서 이미지 URL을 추출합니다.
    1. 먼저, <div class="article-image"> 내부의 <img> 태그를 확인합니다.
    2. 만약 찾지 못하면, Open Graph 메타 태그 (og:image)를 확인합니다.
    
    인자:
      article_url (str): 뉴스 기사 URL
      
    반환:
      str: 이미지 URL (절대 URL) / 이미지가 없으면 None을 반환합니다.
    """
    # 헤더 설정
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/131.0.0.0 Safari/537.36'),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    response = requests.get(article_url, headers=headers)
    response.raise_for_status()  # 요청 실패 시 예외 발생
    
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. <div class="article-image"> 내부의 <img> 태그를 먼저 확인합니다.
    image_container = soup.find('div', class_='article-image')
    if image_container:
        img_tag = image_container.find('img')
        if img_tag:
            img_src = img_tag.get('src')
            if img_src:
                return urljoin(article_url, img_src)
    
    # 2. Open Graph 메타 태그 (og:image)를 이용하여 이미지 URL을 확인합니다.
    og_image_tag = soup.find("meta", property="og:image")
    if og_image_tag:
        og_image = og_image_tag.get("content")
        if og_image:
            return urljoin(article_url, og_image)
    
    # 이미지 URL을 찾지 못한 경우
    return None

def scrape_news_content(article_url):
    """
    주어진 뉴스 기사 URL을 요청하여 본문 내용을 추출합니다.
    최신 HTML 형식에 맞춰 <div class="news_txt ck-content"> 컨테이너 내부의 텍스트를 우선적으로 추출합니다.
    만약 텍스트 내용이 없고 QR코드를 통한 내용이라면 "QR코드를 찍어보세요!" 라는 메시지를 반환합니다.
    
    인자:
      article_url (str): 뉴스 기사 URL
      
    반환:
      str: 기사 내용(본문 텍스트) 또는 "QR코드를 찍어보세요!" 메시지 / 내용이 없으면 None 반환
    """
    # 헤더 설정 (봇 차단 방지용)
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/131.0.0.0 Safari/537.36'),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    response = requests.get(article_url, headers=headers)
    response.raise_for_status()  # 요청 실패 시 예외 발생
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 먼저, 뉴스 내용 박스(news_content_box)가 존재하는지 확인합니다.
    content_box = soup.find('div', class_='news_content_box')
    if content_box:
        news_container = content_box.select_one("div.news_txt.ck-content")
        if news_container:
            # <p> 태그 내부의 텍스트를 우선 추출합니다.
            paragraphs = news_container.find_all("p")
            if paragraphs:
                content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                if content:
                    return content
            # 만약 <p> 태그로는 내용이 추출되지 않으면, 전체 텍스트를 확인합니다.
            content = news_container.get_text(separator="\n", strip=True)
            # 텍스트가 없으면 QR코드 관련 내용으로 판단하여 메시지를 반환합니다.
            if not content:
                return "QR코드를 찍어보세요!"
            return content

    # news_content_box가 없으면 기존 방식대로 진행합니다.
    # 1. div.news_txt.ck-content 내부의 콘텐츠 추출 시도
    news_container = soup.select_one("div.news_txt.ck-content")
    if news_container:
        # 전체 텍스트 추출 또는 <p> 태그만 선택할 수 있습니다.
        paragraphs = news_container.find_all("p")
        if paragraphs:
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)
            if content:
                return content
        # 만약 <p> 태그가 없다면, 컨테이너 전체의 텍스트를 사용합니다.
        content = news_container.get_text(separator="\n", strip=True)
        if content:
            return content

    # 2. 기존 방식: div.article-content 내부의 텍스트 추출
    content_container = soup.find('div', class_='article-content')
    if content_container:
        text = content_container.get_text(separator="\n", strip=True)
        if text:
            return text

    # 3. fallback: inline 스타일 속성이 있는 <p> 태그들 검사
    paragraphs = soup.select('p[style]')
    if paragraphs:
        content = "\n".join(p.get_text(strip=True) for p in paragraphs)
        if content:
            return content

    return None

if __name__ == '__main__':
    # 뉴스 링크 추출 예제
    links = scrape_news_links()
    for news in links:
        print(f"Title: {news['title']}, Link: {news['link']}")
        
    # (예시) 특정 뉴스 기사 URL에 대해 이미지 URL 추출
    # article_url = 'https://www.nongmin.com/article/123'
    # image_url = scrape_news_image(article_url)
    # print(f"Image URL: {image_url}")
