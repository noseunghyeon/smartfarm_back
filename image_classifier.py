import torch
import onnxruntime
import numpy as np
from torchvision import transforms
import io
from PIL import Image
import requests
import tensorflow as tf
import logging
from pydantic import BaseModel
from typing import Dict, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 모델 응답을 위한 Pydantic 모델
class ImageClassificationResponse(BaseModel):
    predicted_class: str
    confidence: float
    class_probabilities: Dict[str, float]
    message: Optional[str] = None

class ImageClassifier:
    def __init__(self):
        self.kiwi_session = self._load_kiwi_model()
        self.chamoe_session = self._load_chamoe_model()
        self.plant_session = self._load_plant_model()
        
        # 클래스 레이블 정의
        self.kiwi_labels = {
            0: "잎_점무늬병",
            1: "잎_정상",
            2: "잎_총채벌레"
        }
        
        self.chamoe_labels = {
            0: "노균병",
            1: "정상",
            2: "흰가루병"
        }
        
        self.plant_labels = {
            0: "비식물",
            1: "식물"
        }

    def _load_kiwi_model(self):
        try:
            url = "https://huggingface.co/jjiw/densenet161-onnx/resolve/main/model.onnx"
            response = requests.get(url)
            model_bytes = io.BytesIO(response.content)
            return onnxruntime.InferenceSession(model_bytes.getvalue())
        except Exception as e:
            logger.error(f"키위 모델 로드 실패: {str(e)}")
            return None

    def _load_chamoe_model(self):
        try:
            url = "https://huggingface.co/jjiw/disease-classifier-onnx/resolve/main/model.onnx"
            response = requests.get(url)
            model_bytes = io.BytesIO(response.content)
            return onnxruntime.InferenceSession(model_bytes.getvalue())
        except Exception as e:
            logger.error(f"참외 모델 로드 실패: {str(e)}")
            return None

    def _load_plant_model(self):
        try:
            url = "https://huggingface.co/jjiw/plant-classifier-h5/resolve/main/model.h5"
            response = requests.get(url)
            model_bytes = io.BytesIO(response.content)
            
            with open('temp_model.h5', 'wb') as f:
                f.write(model_bytes.getvalue())
            
            model = tf.keras.models.load_model('temp_model.h5')
            import os
            os.remove('temp_model.h5')
            
            return model
        except Exception as e:
            logger.error(f"식물 분류 모델 로드 실패: {str(e)}")
            return None

    def preprocess_image(self, image, target_size=(224, 224)):
        """공통 이미지 전처리 함수"""
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        image = image.resize(target_size)
        return image

    async def classify_kiwi(self, image: Image.Image) -> ImageClassificationResponse:
        try:
            if self.kiwi_session is None:
                raise ValueError("키위 모델이 로드되지 않았습니다")

            # 이미지 전처리
            image = self.preprocess_image(image)
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                  std=[0.229, 0.224, 0.225])
            ])
            img_tensor = transform(image).numpy()

            # 예측 수행
            input_name = self.kiwi_session.get_inputs()[0].name
            outputs = self.kiwi_session.run(None, 
                {input_name: img_tensor.reshape(1, 3, 224, 224)})
            probabilities = torch.nn.functional.softmax(torch.tensor(outputs[0][0]), dim=0)
            
            predicted_idx = probabilities.argmax().item()
            confidence = float(probabilities[predicted_idx])

            # 모든 클래스의 확률 계산
            class_probs = {
                self.kiwi_labels[i]: float(probabilities[i])
                for i in range(len(self.kiwi_labels))
            }

            return ImageClassificationResponse(
                predicted_class=self.kiwi_labels[predicted_idx],
                confidence=confidence,
                class_probabilities=class_probs,
                message="키위 질병 분석이 완료되었습니다"
            )

        except Exception as e:
            logger.error(f"키위 분류 오류: {str(e)}")
            raise

    async def classify_chamoe(self, image: Image.Image) -> ImageClassificationResponse:
        try:
            if self.chamoe_session is None:
                raise ValueError("참외 모델이 로드되지 않았습니다")

            # 이미지 전처리
            image = self.preprocess_image(image)
            img_array = np.array(image).astype('float32') / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # 예측 수행
            input_name = self.chamoe_session.get_inputs()[0].name
            outputs = self.chamoe_session.run(None, {input_name: img_array})
            probabilities = torch.nn.functional.softmax(torch.tensor(outputs[0][0]), dim=0)
            
            predicted_idx = probabilities.argmax().item()
            confidence = float(probabilities[predicted_idx])

            # 모든 클래스의 확률 계산
            class_probs = {
                self.chamoe_labels[i]: float(probabilities[i])
                for i in range(len(self.chamoe_labels))
            }

            return ImageClassificationResponse(
                predicted_class=self.chamoe_labels[predicted_idx],
                confidence=confidence,
                class_probabilities=class_probs,
                message="참외 질병 분석이 완료되었습니다"
            )

        except Exception as e:
            logger.error(f"참외 분류 오류: {str(e)}")
            raise

    async def classify_plant(self, image: Image.Image) -> ImageClassificationResponse:
        try:
            if self.plant_session is None:
                raise ValueError("식물 분류 모델이 로드되지 않았습니다")

            # 이미지 전처리
            image = self.preprocess_image(image)
            img_array = np.array(image).astype('float32') / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # 예측 수행
            predictions = self.plant_session.predict(img_array)
            confidence = float(predictions[0][0])
            predicted_idx = 1 if confidence > 0.5 else 0

            # 확률 계산
            class_probs = {
                "비식물": float(confidence),
                "식물": float(1 - confidence)
            }

            return ImageClassificationResponse(
                predicted_class=self.plant_labels[predicted_idx],
                confidence=confidence if predicted_idx == 1 else 1 - confidence,
                class_probabilities=class_probs,
                message="식물 분류가 완료되었습니다"
            )

        except Exception as e:
            logger.error(f"식물 분류 오류: {str(e)}")
            raise

# 싱글톤 인스턴스 생성
classifier = ImageClassifier() 