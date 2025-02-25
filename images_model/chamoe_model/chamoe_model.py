from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from keras.models import load_model
import numpy as np
import uvicorn
import cv2

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모델 로드
plant_model = load_model('images_model/chamoe_model/chamoe_models/plant_classifier.h5')  # 참외 식물 여부 판별 모델
disease_model = load_model('images_model/chamoe_model/chamoe_models/best_disease_classifier.h5')  # 병해 분류 모델

CATEGORIES = ["downy_mildew_chamoe", "healthy_chamoe", "powdery_mildew_chamoe"]

@app.post("/predict")
async def predict_disease(file: UploadFile = File(...)):
    try:
        # 이미지 읽기 및 전처리
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img, (224, 224))  # 모델 입력 크기로 변경
        img_array = np.expand_dims(img_resized, axis=0) / 255.0  # 정규화

        # 1단계: 참외 식물 여부 판별
        plant_prob = float(plant_model.predict(img_array)[0][0])
        
        if plant_prob < 0.5:
            return {
                "success": True,
                "result": "유효하지 않은 이미지",
                "plant_probability": plant_prob,
                "details": "참외 식물이 아닙니다."
            }

        # 2단계: 병해 예측
        disease_pred = disease_model.predict(img_array)[0]
        disease_idx = np.argmax(disease_pred)
        
        # 각 카테고리별 확률
        probabilities = {
            CATEGORIES[i]: float(disease_pred[i]) for i in range(len(CATEGORIES))
        }

        # 한글로 결과 변환
        result_mapping = {
            "downy_mildew_chamoe": "노균병",
            "healthy_chamoe": "정상",
            "powdery_mildew_chamoe": "흰가루병"
        }
        
        result = result_mapping[CATEGORIES[disease_idx]]

        return {
            "success": True,
            "result": result,
            "plant_probability": plant_prob,
            "probabilities": probabilities,
            "details": f"참외 식물 인식 확률: {plant_prob:.2%}\n" +
                      "\n".join([f"{result_mapping.get(cat, cat)} 확률: {prob:.2%}" 
                                for cat, prob in probabilities.items()])
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

