from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
        print(f"Weather API Error: {str(e)}")
        return {"error": str(e)}

@app.get("/predictions/{city}")
async def get_predictions(city: str):
    try:
        from testpython.pricetest import predict_prices
        from utils.apiUrl import fetchWeatherData, processWeatherData
        
        # 날씨 데이터 가져오기
        weather_data = await fetchWeatherData(city)
        processed_weather = processWeatherData(weather_data)
        
        # 예측 수행
        predictions = predict_prices(processed_weather)
        
        return predictions
    except Exception as e:
        print(f"Prediction Error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)