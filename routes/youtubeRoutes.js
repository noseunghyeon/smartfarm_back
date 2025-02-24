const express = require('express');
const router = express.Router();
const { google } = require('googleapis');

// 서버 사이드 캐싱
let cachedVideos = null;
let lastCacheTime = null;
const CACHE_DURATION = 60 * 60 * 1000; // 1시간

router.get('/youtube-videos', async (req, res) => {
  try {
    // 캐시가 유효한 경우 캐시된 데이터 반환
    if (cachedVideos && lastCacheTime && Date.now() - lastCacheTime < CACHE_DURATION) {
      return res.json(cachedVideos);
    }

    const youtube = google.youtube({
      version: 'v3',
      auth: process.env.YOUTUBE_API_KEY
    });

    const response = await youtube.search.list({
      part: 'snippet',
      q: '농업 교육', // 검색어
      maxResults: 3,
      type: 'video'
    });

    // 결과 캐싱
    cachedVideos = response.data.items;
    lastCacheTime = Date.now();

    res.json(cachedVideos);
  } catch (error) {
    console.error('YouTube API error:', error);
    res.status(500).json({ error: 'Failed to fetch YouTube videos' });
  }
});

module.exports = router; 