from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import onnxruntime as ort
import numpy as np
import uvicorn
import cv2
import os

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 현재 파일의 디렉토리 경로를 가져옵니다
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 모델 파일 경로 설정
plant_model_path = os.path.join(BASE_DIR, 'models', 'plant_classifier.onnx')
disease_model_path = os.path.join(BASE_DIR, 'models', 'best_disease_classifier.onnx')

# 모델 파일 존재 여부 확인
if not os.path.exists(plant_model_path):
    raise FileNotFoundError(f"Plant classifier model not found at: {plant_model_path}")
if not os.path.exists(disease_model_path):
    raise FileNotFoundError(f"Disease classifier model not found at: {disease_model_path}")

# ONNX 모델 로드
plant_model = ort.InferenceSession(plant_model_path)
disease_model = ort.InferenceSession(disease_model_path)

CATEGORIES = ["downy_mildew_chamoe", "healthy_chamoe", "powdery_mildew_chamoe"]

@app.post("/predict")
async def predict_disease(file: UploadFile = File(...)):
    try:
        # 이미지 읽기 및 전처리
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img, (224, 224))
        img_array = np.expand_dims(img_resized, axis=0).astype(np.float32) / 255.0

        # 1단계: 참외 식물 여부 판별
        input_name = plant_model.get_inputs()[0].name
        output_name = plant_model.get_outputs()[0].name
        plant_prob = float(plant_model.run([output_name], {input_name: img_array})[0][0][0])
        
        if plant_prob < 0.5:
            return {
                "success": True,
                "result": "유효하지 않은 이미지",
                "plant_probability": plant_prob,
                "details": "참외 식물이 아닙니다."
            }

        # 2단계: 병해 예측
        input_name = disease_model.get_inputs()[0].name
        output_name = disease_model.get_outputs()[0].name
        disease_pred = disease_model.run([output_name], {input_name: img_array})[0][0]
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

