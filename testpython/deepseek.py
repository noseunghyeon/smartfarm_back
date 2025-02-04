import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

#  **다층 퍼셉트론(MLP, Multi-Layer Perceptron)**을 사용하겠습니다. MLP는 신경망의 기본 형태로,
#  여러 개의 은닉층을 통해 비선형 관계를 학습할 수 있습니다.

# 딥러닝 모델 설계
# 라이브러리 임포트: TensorFlow와 Keras를 사용합니다.

# 데이터 전처리: 선형회귀와 동일한 방식으로 데이터를 분할합니다.

# 모델 구성: 입력층, 은닉층, 출력층으로 구성된 신경망을 설계합니다.

# 모델 학습: 데이터를 학습시켜 가격을 예측합니다.

# 모델 평가: R2 점수와 RMSE를 계산하여 모델 성능을 평가합니다.

# 데이터 로드
df = pd.read_csv('../testdata/Total.csv')

# 결측치가 있는 행(가격이 0인 행) 제거
df = df[~(df[['cabbage', 'potato', 'apple', 'onion', 'cucumber', 
           'pepper', 'paprika', 'spinach', 'tomato', 'lettuce']] == 0).any(axis=1)]

# 특성(X)과 타겟(y) 데이터 분리
X = df[['avg temp', 'max temp', 'min temp', 'rainFall']]
vegetables = ['cabbage', 'potato', 'apple', 'onion', 'cucumber', 
              'pepper', 'paprika', 'spinach', 'tomato', 'lettuce']

# 각 농산물별 모델 학습 및 평가
models = {}
scores = {}

for veg in vegetables:
    # 타겟 데이터
    y = df[veg]
    
    # 학습/테스트 데이터 분할
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 딥러닝 모델 구성
    model = Sequential()
    model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))  # 입력층 + 은닉층
    model.add(Dense(32, activation='relu'))  # 은닉층
    model.add(Dense(1, activation='linear'))  # 출력층 (가격 예측)
    
    # 모델 컴파일
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
    
    # 모델 학습
    model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=0)
    
    # 예측
    y_pred = model.predict(X_test).flatten()
    
    # 모델 평가
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    # 결과 저장
    models[veg] = model
    scores[veg] = {'R2': r2, 'RMSE': rmse}
    
    print(f'\n{veg} 예측 결과:')
    print(f'R2 점수: {r2:.4f}')
    print(f'RMSE: {rmse:.2f}')

# 새로운 데이터로 예측하는 예시
new_data = pd.DataFrame({
    'avg temp': [20],
    'max temp': [25],
    'min temp': [15],
    'rainFall': [5]
})

print('\n새로운 데이터에 대한 예측 결과:')
for veg in vegetables:
    predicted_price = models[veg].predict(new_data)[0][0]
    print(f'{veg}: {predicted_price:.2f}원')