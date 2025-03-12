import torch
import onnxruntime
import numpy as np
from torchvision import transforms
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import io
from PIL import Image
import uvicorn
import os
import requests
from fastapi import HTTPException
import logging

# 로깅 설정 추가 (파일 상단에 추가)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 클래스 레이블 정의
CLASS_LABELS = {
    0: "잎_점무늬병",
    1: "잎_정상",
    2: "잎_총채벌레"
}

# ONNX 모델 다운로드
def download_onnx_model():
    model_path = "model.onnx"
    if not os.path.exists(model_path):
        url = "https://huggingface.co/jjiw/densenet161-onnx/resolve/main/model.onnx"
        response = requests.get(url)
        with open(model_path, "wb") as f:
            f.write(response.content)
    return model_path

# ONNX 런타임 세션 생성
model_path = download_onnx_model()
session = onnxruntime.InferenceSession(model_path)

# 이미지 전처리 함수
def preprocess_image(image):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    img_tensor = transform(image)
    return img_tensor.numpy()

# 예측 함수
def predict(image):
    # 이미지 전처리
    input_data = preprocess_image(image)
    
    # 입력 이름 가져오기
    input_name = session.get_inputs()[0].name
    
    # ONNX 모델로 예측 수행
    outputs = session.run(None, {input_name: input_data.reshape(1, 3, 224, 224)})
    probabilities = torch.nn.functional.softmax(torch.tensor(outputs[0][0]), dim=0)
    predicted_class_idx = probabilities.argmax().item()
    
    # 클래스 레이블 가져오기
    predicted_class_label = CLASS_LABELS.get(predicted_class_idx, f"알 수 없는 클래스 {predicted_class_idx}")
    confidence = probabilities[predicted_class_idx].item()
    
    return {
        "class": predicted_class_label,
        "confidence": float(confidence),
        "class_index": predicted_class_idx
    }

# 테스트용 엔드포인트 추가
@app.get("/test")
async def test():
    return {"message": "Server is running"}

# FastAPI 엔드포인트
@app.post("/kiwi_predict")
async def kiwi_predict(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}")  # 로깅 추가
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        # RGBA를 RGB로 변환
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        result = predict(image)
        logger.info(f"Prediction result: {result}")  # 로깅 추가
        return result
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")  # 에러 로깅
        raise HTTPException(status_code=400, detail=str(e))

# 메인 실행 부분 수정
if __name__ == "__main__":
    try:
        port = 8000  # 포트 변경
        logger.info("="*50)
        logger.info(f"Starting Kiwi Model Server on port {port}")
        logger.info(f"API documentation available at: http://localhost:{port}/docs")
        logger.info(f"Test endpoint available at: http://localhost:{port}/test")
        logger.info("="*50)
        
        uvicorn.run(
            app,
            host="127.0.0.1",  # localhost로 변경
            port=port,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        raise