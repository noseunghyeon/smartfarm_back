from keras.models import load_model
from keras.preprocessing import image
import numpy as np

# 모델 로드
downy_mildew_model = load_model('images_farm/downy.model.keras')  # 노균병 모델
powdery_mildew_model = load_model('images_farm/powdery_model.keras')  # 흰가루병 모델

# 테스트할 이미지 경로 (구글 드라이브에 있는 파일 또는 로컬 경로)
test_image_paths = [
    'images_farm/test_images/downy_mildew1.jpg',
    'images_farm/test_images/downy_mildew2.jpg',
    'images_farm/test_images/downy_mildew3.jpg',
    'images_farm/test_images/healthy1.jpg',
    'images_farm/test_images/healthy2.jpg',
    'images_farm/test_images/healthy3.jpg',
    'images_farm/test_images/healthy4.jpg',
    'images_farm/test_images/powdery_mildew1.jpg',
    'images_farm/test_images/powdery_mildew2.jpg',
    'images_farm/test_images/powdery_mildew3.jpg'
]

# 이미지 로드 및 전처리 함수
def load_and_preprocess_images(image_paths):
    images = []
    for img_path in image_paths:
        img = image.load_img(img_path, target_size=(64, 64))
        img_array = image.img_to_array(img) / 255.0  # 이미지를 배열로 변환하고 정규화
        images.append(img_array)
    return np.array(images)

# 이미지 로드 및 전처리
test_images = load_and_preprocess_images(test_image_paths)

# 예측 수행
downy_mildew_predictions = downy_mildew_model.predict(test_images)
powdery_mildew_predictions = powdery_mildew_model.predict(test_images)

# 예측 결과 비교 후 최종 예측 선택
for i in range(len(test_image_paths)):
    downy_mildew_prob = downy_mildew_predictions[i][0]  # 노균병 예측 확률
    powdery_mildew_prob = powdery_mildew_predictions[i][0]  # 흰가루병 예측 확률

    # 정상 판별: 두 모델이 모두 0.5 미만일 경우 "정상"으로 예측
    if downy_mildew_prob < 0.5 and powdery_mildew_prob < 0.5:
        final_result = "정상"
    else:
        # 더 높은 확률을 보인 모델을 기준으로 최종 예측
        if downy_mildew_prob > powdery_mildew_prob:
            final_result = "노균병"
        else:
            final_result = "흰가루병"  # 흰가루병 모델의 확률이 더 높을 때

    print(f"이미지 {i+1} ({test_image_paths[i]}):")
    print(f"  - 노균병 예측 확률: {downy_mildew_prob:.5f}")
    print(f"  - 흰가루병 예측 확률: {powdery_mildew_prob:.5f}")
    print(f"  - 최종 예측: {final_result}")
    print("-" * 50)

