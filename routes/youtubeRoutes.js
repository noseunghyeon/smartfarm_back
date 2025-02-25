const express = require('express');
const router = express.Router();
const { google } = require('googleapis');

// 서버 사이드 캐싱
let cachedVideos = null;
let lastCacheTime = null;
const CACHE_DURATION = 60 * 60 * 1000; // 1시간

router.get('/youtube-videos', async (req, res) => {
  // API 호출 비활성화: 임시 데이터 반환
  return res.json([
    {
      id: { videoId: 'temp1' },
      snippet: {
        title: '임시 영상 1',
        description: '임시 설명 1',
        thumbnails: {
          medium: {
            url: 'https://via.placeholder.com/320x180'
          }
        }
      }
    },
    {
      id: { videoId: 'temp2' },
      snippet: {
        title: '임시 영상 2',
        description: '임시 설명 2',
        thumbnails: {
          medium: {
            url: 'https://via.placeholder.com/320x180'
          }
        }
      }
    },
    {
      id: { videoId: 'temp3' },
      snippet: {
        title: '임시 영상 3',
        description: '임시 설명 3',
        thumbnails: {
          medium: {
            url: 'https://via.placeholder.com/320x180'
          }
        }
      }
    }
  ]);

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