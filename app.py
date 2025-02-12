from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uvicorn

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/weather")
async def get_weather(city: str):
    try:
        from utils.apiUrl import fetchWeatherData
        weather_data = await fetchWeatherData(city)
        return weather_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/predictions/{city}")
async def get_predictions(city: str):
    try:
        from utils.apiUrl import fetchWeatherData
        from testpython.pricetest_v2 import predict_prices
        
        # 날씨 데이터 가져오기
        weather_data = await fetchWeatherData(city)
        
        # 가격 예측하기 (processed_data 사용)
        predictions = predict_prices({
            'current': weather_data['current'],
            'tomorrow': weather_data['tomorrow'],
            'weekly': weather_data['weekly']
        })
        
        return {
            "predictions": predictions,
            "weather_data": weather_data['raw']
        }
    except Exception as e:
        print(f"Error in predictions: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("Server is running on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)