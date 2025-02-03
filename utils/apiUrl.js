const axios = require('axios');
const API_KEY = "7f1fcc5273319b5ceb9fc021843fb291";
const BASE_URL = "http://api.openweathermap.org/data/2.5/forecast";

// 날씨 데이터를 가져오는 함수
async function fetchWeatherData(city) {
  try {
    // URL 인코딩 추가
    const encodedCity = encodeURIComponent(city);
    const url = `${BASE_URL}?q=${encodedCity}&appid=${API_KEY}&units=metric&lang=kr`;
    
    console.log('요청 URL:', url); // 디버깅을 위한 로그
    
    const response = await axios.get(url);
    
    return response.data;
  } catch (error) {
    console.error('날씨 데이터를 가져오는데 실패했습니다:', error);
    throw error;
  }
}

module.exports = {
  API_KEY,
  BASE_URL,
  fetchWeatherData,
};
