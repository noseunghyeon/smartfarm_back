const path = require('path');
const dotenv = require('dotenv');

// 환경 변수 로딩 경로 수정 (back 폴더 기준)
const envPath = path.resolve(__dirname, '../.env');
console.log('환경 변수 파일 경로:', envPath);

// 환경 변수 로딩
const result = dotenv.config({ path: envPath });
if (result.error) {
    console.error('환경 변수 로딩 에러:', result.error);
}

const axios = require("axios");

const API_KEY = process.env.WEATHER_API_KEY;
console.log("API KEY 확인:", API_KEY); // API 키가 제대로 로드되는지 확인
const BASE_URL = "http://api.openweathermap.org/data/2.5/forecast";

// 날씨 데이터를 가져오는 함수
async function fetchWeatherData(city) {
  try {
    const encodedCity = encodeURIComponent(city);
    const url = `${BASE_URL}?q=${encodedCity}&appid=${API_KEY}&units=metric&lang=kr`;

    console.log("요청 URL:", url);
    const response = await axios.get(url);
    
    // 현재 날씨 데이터 수정
    const currentWeather = {
      도시: response.data.city.name,
      현재기온: response.data.list[0].main.temp,      // 현재 기온
      최고기온: response.data.list[0].main.temp_max,
      최저기온: response.data.list[0].main.temp_min,
      습도: response.data.list[0].main.humidity,
      날씨설명: response.data.list[0].weather[0].description,
      강수량: response.data.list[0].rain ? response.data.list[0].rain['3h'] : 0
    };

    // 내일 날씨 데이터 처리
    const tomorrowWeather = {
      최고기온: Math.max(...response.data.list.slice(8, 16).map(item => item.main.temp_max)), // 내일의 최고기온
      최저기온: Math.min(...response.data.list.slice(8, 16).map(item => item.main.temp_min)), // 내일의 최저기온
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

    console.log("현재 날씨:", currentWeather);
    console.log("내일 날씨:", tomorrowWeather);
    console.log("주간 날씨:", weeklyWeather);

    return {
      current: currentWeather,
      tomorrow: tomorrowWeather,
      weekly: weeklyWeather,
      raw: response.data // 원본 데이터도 포함
    };
  } catch (error) {
    console.error("날씨 데이터를 가져오는데 실패했습니다:", error);
    throw error;
  }
}

// 날씨 데이터를 가공하는 함수 수정
function processWeatherData(weatherData) {
  try {
    const weatherList = [];

    // 현재 날씨 데이터
    const current = {
      'avg temp': (weatherData.current.현재기온 + weatherData.current.최고기온 + weatherData.current.최저기온) / 3,
      'max temp': weatherData.current.최고기온,
      'min temp': weatherData.current.최저기온,
      'rainFall': weatherData.current.강수량 || 0
    };
    weatherList.push(current);

    // 내일 날씨 데이터
    const tomorrow = {
      'avg temp': (weatherData.tomorrow.최고기온 + weatherData.tomorrow.최저기온) / 2,
      'max temp': weatherData.tomorrow.최고기온,
      'min temp': weatherData.tomorrow.최저기온,
      'rainFall': weatherData.tomorrow.강수량 || 0
    };
    weatherList.push(tomorrow);

    // 주간 날씨 데이터
    const weekly = weatherData.weekly.map(day => ({
      'avg temp': (day.최고기온 + day.최저기온) / 2,
      'max temp': day.최고기온,
      'min temp': day.최저기온,
      'rainFall': day.강수량 || 0
    }));
    weatherList.push(...weekly);

    return {
      current: current,
      tomorrow: tomorrow,
      weekly: weekly
    };
  } catch (error) {
    console.error('날씨 데이터 처리 중 오류 발생:', error);
    throw error;
  }
}

// 농산물 가격 예측 데이터를 가져오는 함수
async function fetchPricePredictions(city) {
  try {
    const response = await axios.get(`http://localhost:8000/predictions/${encodeURIComponent(city)}`);
    return response.data;
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
