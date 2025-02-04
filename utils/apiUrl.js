require("dotenv").config();
const axios = require("axios");

const API_KEY = process.env.WEATHER_API_KEY;
const BASE_URL = "http://api.openweathermap.org/data/2.5/forecast";

// 날씨 데이터를 가져오는 함수
async function fetchWeatherData(city) {
  try {
    // URL 인코딩 추가
    const encodedCity = encodeURIComponent(city);
    const url = `${BASE_URL}?q=${encodedCity}&appid=${API_KEY}&units=metric&lang=kr`;

    console.log("요청 URL:", url); // 디버깅을 위한 로그

    const response = await axios.get(url);

    return response.data;
  } catch (error) {
    console.error("날씨 데이터를 가져오는데 실패했습니다:", error);
    throw error;
  }
}

// 농산물 가격 예측 데이터를 가져오는 함수
async function fetchPricePredictions() {
  try {
    // Python 스크립트 실행 결과를 가져오는 로직
    const predictions = {
      cabbage: 3500,
      potato: 2800,
      apple: 4500,
      onion: 2000,
      cucumber: 3000,
      pepper: 3800,
      paprika: 4200,
      spinach: 2500,
      tomato: 3200,
      lettuce: 2700,
      // R2 점수
      cabbage_r2: 0.85,
      potato_r2: 0.82,
      apple_r2: 0.88,
      onion_r2: 0.81,
      cucumber_r2: 0.83,
      pepper_r2: 0.84,
      paprika_r2: 0.86,
      spinach_r2: 0.80,
      tomato_r2: 0.85,
      lettuce_r2: 0.82
    };

    return predictions;
  } catch (error) {
    console.error('가격 예측 데이터를 가져오는데 실패했습니다:', error);
    throw error;
  }
}

module.exports = {
  API_KEY,
  BASE_URL,
  fetchWeatherData,
  fetchPricePredictions
};
