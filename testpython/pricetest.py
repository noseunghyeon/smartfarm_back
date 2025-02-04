import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

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
    
    # 모델 학습
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # 예측
    y_pred = model.predict(X_test)
    
    # 모델 평가
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    # 결과 저장
    models[veg] = model
    scores[veg] = {'R2': r2, 'RMSE': rmse}
    
    print(f'\n{veg} 예측 결과:')
    print(f'R2 점수: {r2:.4f}')
    print(f'RMSE: {rmse:.2f}')
    print('계수:', dict(zip(['평균기온', '최고기온', '최저기온', '강수량'], 
                         model.coef_.round(2))))
    print('절편:', round(model.intercept_, 2))

# 새로운 데이터로 예측하는 예시
new_data = pd.DataFrame({
    'avg temp': [20],
    'max temp': [25],
    'min temp': [15],
    'rainFall': [5]
})

print('\n새로운 데이터에 대한 예측 결과:')
for veg in vegetables:
    predicted_price = models[veg].predict(new_data)[0]
    print(f'{veg}: {predicted_price:.2f}원')
