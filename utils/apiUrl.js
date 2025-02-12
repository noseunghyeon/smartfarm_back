const path = require('path');
const dotenv = require('dotenv');
const axios = require("axios");

// 환경 변수 로딩
const envPath = path.resolve(__dirname, '../.env');
dotenv.config({ path: envPath });

const API_KEY = process.env.WEATHER_API_KEY;
const BASE_URL = "http://api.openweathermap.org/data/2.5/forecast";

// 날씨 데이터를 가져오는 함수
async function fetchWeatherData(city) {
  try {
    const encodedCity = encodeURIComponent(city);
    const url = `${BASE_URL}?q=${encodedCity}&appid=${API_KEY}&units=metric&lang=kr`;

    const response = await axios.get(url);
    
    // 현재 날씨 데이터 수정
    const currentWeather = {
      도시: response.data.city.name,
      현재기온: response.data.list[0].main.temp,
      최고기온: response.data.list[0].main.temp_max,
      최저기온: response.data.list[0].main.temp_min,
      습도: response.data.list[0].main.humidity,
      날씨설명: response.data.list[0].weather[0].description,
      강수량: response.data.list[0].rain ? response.data.list[0].rain['3h'] : 0
    };

    // 내일 날씨 데이터 처리
    const tomorrowWeather = {
      최고기온: Math.max(...response.data.list.slice(8, 16).map(item => item.main.temp_max)),
      최저기온: Math.min(...response.data.list.slice(8, 16).map(item => item.main.temp_min)),
      습도: response.data.list[8].main.humidity,
      날씨설명: response.data.list[8].weather[0].description,
      강수량: response.data.list[8].rain ? response.data.list[8].rain['3h'] : 0
    };

    // 주간 날씨 데이터 처리
    const weeklyWeather = [];
    for (let i = 0; i < 40; i += 8) {
      const dayData = response.data.list.slice(i, i + 8);
      const date = new Date(dayData[0].dt * 1000);
      
      weeklyWeather.push({
        날짜: date.toLocaleDateString('ko-KR'),
        최고기온: Math.max(...dayData.map(item => item.main.temp_max)),
        최저기온: Math.min(...dayData.map(item => item.main.temp_min)),
        습도: dayData[0].main.humidity,
        날씨설명: dayData[0].weather[0].description,
        강수량: dayData[0].rain ? dayData[0].rain['3h'] : 0
      });
    }

    return {
      current: currentWeather,
      tomorrow: tomorrowWeather,
      weekly: weeklyWeather,
      raw: response.data
    };
  } catch (error) {
    console.error("날씨 데이터를 가져오는데 실패했습니다:", error);
    throw error;
  }
}

module.exports = {
  API_KEY,
  BASE_URL,
  fetchWeatherData
};
