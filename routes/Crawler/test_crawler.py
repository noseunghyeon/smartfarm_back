import unittest
from unittest.mock import patch, Mock
from back.routes.Crawler.crawler import scrape_news_links, scrape_news_image, scrape_news_content
from urllib.parse import urljoin

class TestScrapeNewsLinks(unittest.TestCase):
    @patch('back.routes.Crawler.crawler.requests.get')
    def test_returns_news_links(self, mock_get):
        # 테스트용 HTML 스텁 (새로운 구조: 단일 페이지)
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
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response

        # 함수 호출 (pages 기본값=1)
        news_links = scrape_news_links()

        # "/other" 링크는 필터되어야 하므로 실제 크롤링 결과는 2건이어야 합니다.
        self.assertIsInstance(news_links, list)
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
    def test_scrape_news_links_multiple_pages(self, mock_get):
        # 테스트용 HTML 스텁 - 페이지 1
        html_stub_page1 = '''
        <html>
            <body>
                <div class="news_list news_content">
                    <div class="list_cont">
                        <div data-layout-area="LEFT_NEWS_LIST">
                            <ul class="common_list">
                                <li>
                                    <a href="/article/111">
                                        <div class="txt_wrap">
                                            <pre class="tit">페이지1 - 기사 1</pre>
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
        # 테스트용 HTML 스텁 - 페이지 2
        html_stub_page2 = '''
        <html>
            <body>
                <div class="news_list news_content">
                    <div class="list_cont">
                        <div data-layout-area="LEFT_NEWS_LIST">
                            <ul class="common_list">
                                <li>
                                    <a href="/article/222">
                                        <div class="txt_wrap">
                                            <pre class="tit">페이지2 - 기사 2</pre>
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
        # 두 페이지에 대해 모의 응답 객체 생성 (side_effect 사용)
        mock_response_page1 = Mock()
        mock_response_page1.text = html_stub_page1
        mock_response_page1.raise_for_status = lambda: None

        mock_response_page2 = Mock()
        mock_response_page2.text = html_stub_page2
        mock_response_page2.raise_for_status = lambda: None

        # 첫 번째 호출은 페이지 1, 두 번째 호출은 페이지 2에 사용됩니다.
        mock_get.side_effect = [mock_response_page1, mock_response_page2]

        # 함수 호출 (pages=2)
        news_links = scrape_news_links("https://www.nongmin.com/list/19", pages=2)

        # 두 페이지의 결과가 모두 합쳐져야 하므로 총 2건이어야 합니다.
        self.assertEqual(len(news_links), 2)
        self.assertEqual(news_links[0]['title'], '페이지1 - 기사 1')
        expected_link1 = urljoin('https://www.nongmin.com/list/19', '/article/111')
        self.assertEqual(news_links[0]['link'], expected_link1)
        self.assertEqual(news_links[1]['title'], '페이지2 - 기사 2')
        expected_link2 = urljoin('https://www.nongmin.com/list/19', '/article/222')
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
        
        self.assertEqual(content, "이 기사의 내용입니다.")

if __name__ == '__main__':
    unittest.main()