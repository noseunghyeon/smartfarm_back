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
                raw_data = await response.json()
                
                # 날씨 데이터 처리
                processed_data = processWeatherData(raw_data)
                return processed_data
                
    except Exception as e:
        print(f"날씨 데이터를 가져오는데 실패했습니다: {str(e)}")
        raise e

def processWeatherData(weatherData):
    try:
        list_data = weatherData.get('list', [])
        if not list_data:
            raise ValueError("날씨 데이터가 비어있습니다")

        # 현재, 내일, 주간 데이터 처리
        current_data = list_data[0]
        tomorrow_data = list_data[1]
        weekly_data = list_data[1:6]  # 5일치 데이터

        # 데이터 형식 변환
        processed = {
            'current': {
                'avg temp': current_data['main']['temp'],
                'max temp': current_data['main']['temp_max'],
                'min temp': current_data['main']['temp_min'],
                'rainFall': current_data.get('rain', {}).get('3h', 0)
            },
            'tomorrow': {
                'avg temp': tomorrow_data['main']['temp'],
                'max temp': tomorrow_data['main']['temp_max'],
                'min temp': tomorrow_data['main']['temp_min'],
                'rainFall': tomorrow_data.get('rain', {}).get('3h', 0)
            },
            'weekly': [
                {
                    'avg temp': day['main']['temp'],
                    'max temp': day['main']['temp_max'],
                    'min temp': day['main']['temp_min'],
                    'rainFall': day.get('rain', {}).get('3h', 0)
                }
                for day in weekly_data
            ],
            'raw': weatherData  # 원본 데이터도 유지
        }
        
        return processed
        
    except Exception as e:
        print(f'날씨 데이터 처리 중 오류 발생: {str(e)}')
        raise e 