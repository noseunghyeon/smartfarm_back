const express = require('express');
const router = express.Router();
const { fetchWeatherData, fetchPricePredictions } = require('../utils/apiUrl');

router.get('/weather', async (req, res) => {
  try {
    const { city } = req.query;
    console.log('요청된 도시:', city); // 디버깅을 위한 로그
    
    if (!city) {
      return res.status(400).json({ error: '도시 이름이 필요합니다.' });
    }
    
    const weatherData = await fetchWeatherData(city);
    res.json(weatherData);
  } catch (error) {
    console.error('라우트 에러:', error); // 디버깅을 위한 로그
    res.status(500).json({ 
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

router.get('/predictions', async (req, res) => {
  try {
    const predictions = await fetchPricePredictions();
    res.json(predictions);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router; 