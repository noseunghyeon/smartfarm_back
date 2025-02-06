from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from testpython.pricetest import predict_prices

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/predictions")
async def get_predictions(
    avg_temp: float = 20.0,
    max_temp: float = 25.0,
    min_temp: float = 15.0,
    rainfall: float = 5.0
):
    temp_data = pd.DataFrame({
        'avg temp': [avg_temp],
        'max temp': [max_temp],
        'min temp': [min_temp],
        'rainFall': [rainfall]
    })
    
    predictions = predict_prices(temp_data)
    return predictions 