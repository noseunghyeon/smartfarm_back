from keras.models import load_model
from keras.preprocessing import image
import numpy as np

# 모델 로드
model = load_model('images_farm/chamoe_model.keras')

# 예측할 이미지 로드
img_path = 'images_farm/test_images/test4.jpg'  # 테스트 이미지 경로
img = image.load_img(img_path, target_size=(64, 64))

# 이미지 전처리
img_array = image.img_to_array(img) / 255.0  # 이미지를 배열로 변환하고 정규화
img_array = np.expand_dims(img_array, axis=0)  # 배치 차원 추가

# 예측
prediction = model.predict(img_array)
prediction = (prediction > 0.5).astype(int)  # 0.5를 기준으로 이진 분류

# 예측 결과 출력
if prediction == 0:
    print("예측 결과: 정상")
else:
    print("예측 결과: 노균병")
