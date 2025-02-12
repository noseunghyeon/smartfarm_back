import os
from dotenv import load_dotenv
import aiohttp
import json

# 환경 변수 로딩
load_dotenv()

API_KEY = os.getenv('WEATHER_API_KEY')
BASE_URL = "http://api.openweathermap.org/data/2.5/forecast"

async def fetchWeatherData(city):
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                'q': city,
                'appid': API_KEY,
                'units': 'metric',
                'lang': 'kr'
            }
            
            async with session.get(BASE_URL, params=params) as response:
                data = await response.json()
                return data
                
    except Exception as e:
        print(f"날씨 데이터를 가져오는데 실패했습니다: {str(e)}")
        raise e

def processWeatherData(weatherData):
    try:
        # 현재 날씨 데이터
        current = {
            'avg temp': weatherData['list'][0]['main']['temp'],
            'max temp': weatherData['list'][0]['main']['temp_max'],
            'min temp': weatherData['list'][0]['main']['temp_min'],
            'rainFall': weatherData['list'][0].get('rain', {}).get('3h', 0)
        }

        # 내일 날씨 데이터 (24시간 후)
        tomorrow = {
            'avg temp': weatherData['list'][8]['main']['temp'],
            'max temp': weatherData['list'][8]['main']['temp_max'],
            'min temp': weatherData['list'][8]['main']['temp_min'],
            'rainFall': weatherData['list'][8].get('rain', {}).get('3h', 0)
        }

        # 주간 날씨 데이터
        weekly = []
        for i in range(0, 5):  # 5일치 데이터
            day_data = {
                'avg temp': weatherData['list'][i*8]['main']['temp'],
                'max temp': weatherData['list'][i*8]['main']['temp_max'],
                'min temp': weatherData['list'][i*8]['main']['temp_min'],
                'rainFall': weatherData['list'][i*8].get('rain', {}).get('3h', 0)
            }
            weekly.append(day_data)
        
        return {
            'current': current,
            'tomorrow': tomorrow,
            'weekly': weekly,
            'raw': weatherData
        }
    except Exception as e:
        print(f'날씨 데이터 처리 중 오류 발생: {str(e)}')
        raise e 