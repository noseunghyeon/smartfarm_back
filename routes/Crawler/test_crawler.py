import unittest
from unittest.mock import patch, Mock
from back.routes.Crawler.crawler import scrape_news_links, scrape_news_image, scrape_news_content
from urllib.parse import urljoin

class TestScrapeNewsLinks(unittest.TestCase):
    @patch('back.routes.Crawler.crawler.requests.get')
    def test_returns_news_links(self, mock_get):
        # 테스트용 HTML 스텁 (새로운 구조)
        html_stub = '''
        <html>
            <body>
                <div class="news_list news_content">
                    <div class="list_cont">
                        <div data-layout-area="LEFT_NEWS_LIST" data-layout-area-cnt="1">
                            <ul class="common_list">
                                <li>
                                    <a href="/article/123">
                                        <div class="txt_wrap">
                                            <pre class="tit">뉴스 기사 1</pre>
                                        </div>
                                    </a>
                                </li>
                                <li>
                                    <a href="/article/456">
                                        <div class="txt_wrap">
                                            <pre class="tit">기사 2</pre>
                                        </div>
                                    </a>
                                </li>
                                <li>
                                    <a href="/other">
                                        <div class="txt_wrap">
                                            <pre class="tit">다른 링크</pre>
                                        </div>
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        '''
        # 모의 응답 객체 생성
        mock_response = Mock()
        mock_response.text = html_stub
        # 예외 없이 통과하게 하기 위한 설정
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response

        # 함수 호출
        news_links = scrape_news_links()

        # 뉴스 관련 조건에 맞게 필터링 되었는지 확인
        self.assertIsInstance(news_links, list)
        # "/other" 링크는 필터되어야 하므로 실제 크롤링 결과는 2건이어야 합니다.
        self.assertEqual(len(news_links), 2)
        # 첫 번째 기사 제목과 링크 확인
        self.assertEqual(news_links[0]['title'], '뉴스 기사 1')
        expected_link = urljoin('https://www.nongmin.com/list/19', '/article/123')
        self.assertEqual(news_links[0]['link'], expected_link)
        # 두 번째 기사 제목 확인
        self.assertEqual(news_links[1]['title'], '기사 2')
        expected_link2 = urljoin('https://www.nongmin.com/list/19', '/article/456')
        self.assertEqual(news_links[1]['link'], expected_link2)

    @patch('back.routes.Crawler.crawler.requests.get')
    def test_scrape_news_image_returns_url(self, mock_get):
        # 뉴스 기사 상세페이지 HTML 스텁 (이미지 포함)
        article_html = '''
        <html>
          <body>
            <div class="article-image">
              <img src="/images/news_img.jpg" alt="news image">
            </div>
          </body>
        </html>
        '''
        # 모의 응답 객체 생성
        mock_response = Mock()
        mock_response.text = article_html
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response
        
        article_url = "https://www.nongmin.com/article/123"
        image_url = scrape_news_image(article_url)
        
        expected_image_url = urljoin(article_url, "/images/news_img.jpg")
        self.assertEqual(image_url, expected_image_url)

    @patch('back.routes.Crawler.crawler.requests.get')
    def test_scrape_news_image_no_image(self, mock_get):
        # 뉴스 기사 상세페이지 HTML 스텁 (이미지 미포함)
        article_html = '''
        <html>
          <body>
             <p>이 기사는 이미지가 없습니다.</p>
          </body>
        </html>
        '''
        mock_response = Mock()
        mock_response.text = article_html
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response
        
        article_url = "https://www.nongmin.com/article/456"
        image_url = scrape_news_image(article_url)
        self.assertIsNone(image_url)

# 기존 테스트 외에 콘텐츠 추출에 대한 테스트 추가
class TestScrapeNewsContent(unittest.TestCase):
    @patch('back.routes.Crawler.crawler.requests.get')
    def test_scrape_news_content_returns_content(self, mock_get):
        # 기사 상세페이지 HTML 스텁 (article-content 포함)
        article_html = '''
        <html>
          <body>
            <div class="article-content">
              <p>이 기사의 내용입니다.</p>
            </div>
          </body>
        </html>
        '''
        mock_response = Mock()
        mock_response.text = article_html
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response
        
        article_url = "https://www.nongmin.com/article/123"
        content = scrape_news_content(article_url)
        
        # HTML 태그가 제거된 순수 텍스트를 비교합니다.
        self.assertEqual(content, "이 기사의 내용입니다.")

if __name__ == '__main__':
    unittest.main()