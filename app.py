from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# pricetest.py의 예측 로직 import

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/predictions")
async def get_predictions():
    # pricetest.py의 예측 결과를 반환
    predictions = {
        "cabbage": predicted_price_cabbage,
        "potato": predicted_price_potato,
        # ... 다른 농산물들의 예측 가격
        "cabbage_r2": r2_score_cabbage,
        "potato_r2": r2_score_potato,
        # ... 다른 농산물들의 R2 점수
    }
    return predictions 