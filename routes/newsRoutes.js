const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const router = express.Router();
require('dotenv').config();

router.get('/news', async (req, res) => {
  try {
    console.log('Naver API 요청 시작');
    console.log('Client ID:', process.env.NAVER_CLIENT_ID); // 실제 운영 환경에서는 제거
    
    const response = await axios.get('https://openapi.naver.com/v1/search/news.json', {
      params: {
        query: '농산물',  // 검색어
        display: 3,      // 결과 개수
        sort: 'date'     // 최신순 정렬
      },
      headers: {
        'X-Naver-Client-Id': process.env.NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': process.env.NAVER_CLIENT_SECRET
      }
    });

    console.log('API 응답 성공:', response.status);
    console.log('데이터 샘플:', response.data.items[0]); // 첫 번째 뉴스 항목 확인

    // 각 뉴스 항목에 대해 이미지 추출
    const newsWithImages = await Promise.all(
      response.data.items.map(async (item) => {
        try {
          // 원본 기사 페이지 가져오기
          const articleResponse = await axios.get(item.link);
          const $ = cheerio.load(articleResponse.data);
          
          // og:image 메타 태그에서 이미지 URL 추출
          let imageUrl = $('meta[property="og:image"]').attr('content');
          
          // og:image가 없다면 첫 번째 이미지 태그 시도
          if (!imageUrl) {
            imageUrl = $('img').first().attr('src');
          }

          return {
            ...item,
            imageUrl: imageUrl || null
          };
        } catch (error) {
          console.error(`Failed to fetch image for article: ${item.link}`, error);
          return {
            ...item,
            imageUrl: null
          };
        }
      })
    );

    res.json(newsWithImages);
  } catch (error) {
    console.error('News API Error:', error);
    res.status(500).json({ error: '뉴스를 불러오는데 실패했습니다.' });
  }
});

module.exports = router; 