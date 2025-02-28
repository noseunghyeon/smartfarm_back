from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uvicorn

# try:
#     from images_model.chamoe_model.chamoe_model import predict_disease
# except ImportError as e:
#     print(f"Import Error: {e}")
from utils.apiUrl import KOREAN_CITIES
from test import get_price_data, get_satellite_data

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/cities")
async def get_cities():
    """사용 가능한 도시 목록을 반환합니다."""
    return {
        "success": True,
        "data": {
            "cities": list(KOREAN_CITIES.keys()),
            "mapping": KOREAN_CITIES
        },
        "message": "도시 목록을 성공적으로 가져왔습니다"
    }

@app.get("/weather")
async def get_weather(city: str):
    try:
        if not city:
            raise ValueError("도시명이 입력되지 않았습니다")
            
        if city not in KOREAN_CITIES and city not in KOREAN_CITIES.values():
            raise ValueError("지원하지 않는 도시입니다")
            
        from utils.apiUrl import fetchWeatherData
        weather_data = await fetchWeatherData(city)
        
        return {
            "success": True,
            "data": weather_data,
            "message": "날씨 데이터를 성공적으로 가져왔습니다"
        }
    except Exception as e:
        print(f"Weather API Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "날씨 데이터를 가져오는데 실패했습니다"
        }

@app.post("/predict")
async def predict_chamoe(file: UploadFile = File(...)):
    try:
        result = await predict_disease(file)
        return result
    except Exception as e:
        print(f"Prediction Error: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/predictions/{crop}/{city}")
async def get_predictions(crop: str, city: str):
    try:
        from utils.apiUrl import fetchWeatherData
        
        # 작물에 따른 예측 모듈 선택
        if crop == "cabbage":
            from testpython.cabbage import predict_prices
        elif crop == "apple":
            from testpython.appleprice import predict_prices
        elif crop == "onion":
            from testpython.onion2 import predict_prices
        elif crop == "potato":
            from testpython.potato2 import predict_prices
        elif crop == "cucumber":
            from testpython.cucumber2 import predict_prices
        elif crop == "tomato":
            from testpython.tomato2 import predict_prices
        elif crop == "spinach":
            from testpython.spinach2 import predict_prices
        elif crop == "strawberry":
            from testpython.strawberry import predict_prices
        else:
            raise ValueError("지원하지 않는 작물입니다")
        
        weather_data = await fetchWeatherData(city)
        predictions = predict_prices(weather_data)
        
        if 'error' in predictions:
            raise Exception(predictions['error'])
            
        return {
            "predictions": predictions,
            "weather_data": weather_data['raw']
        }
    except Exception as e:
        print(f"Error in predictions: {str(e)}")
        return {"error": str(e)}

@app.get("/api/satellite")
async def get_satellite():
    """한반도 위성 구름 이미지 정보를 가져옵니다."""
    try:
        result = get_satellite_data()
        if result is None:
            raise HTTPException(status_code=500, detail="위성 데이터를 가져오는데 실패했습니다")
        return {
            "success": True,
            "data": result,
            "message": "위성 이미지 데이터를 성공적으로 가져왔습니다"
        }
    except Exception as e:
        print(f"Satellite API Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "위성 이미지 데이터를 가져오는데 실패했습니다"
        }

@app.get("/api/price")
async def get_price():
    """농산물 가격 정보를 반환합니다."""
    try:
        result = get_price_data()
        if result is None:
            raise HTTPException(status_code=500, detail="데이터를 가져오는데 실패했습니다")
        return {
            "success": True,
            "data": result,
            "message": "가격 데이터를 성공적으로 가져왔습니다"
        }
    except Exception as e:
        print(f"Price API Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "가격 데이터를 가져오는데 실패했습니다"
        }

if __name__ == "__main__":
    print("Server is running on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)