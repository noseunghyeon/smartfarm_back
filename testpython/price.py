import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import sys
import json
import os
from datetime import datetime, timedelta

def create_price_predictor(crop_name):
    try:
        # 현재 파일의 절대 경로를 기준으로 CSV 파일 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(os.path.dirname(current_dir), 'testdata', 'Total_v2.csv')
        
        # CSV 파일 읽기
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # 가격에서 쉼표 제거하고 숫자로 변환
        df[crop_name] = df[crop_name].astype(str).str.replace(',', '').astype(float)

        # 결측치가 있는 행(가격이 0인 행) 제거
        df = df[df[crop_name] != 0]

        # 날짜 특성 추가
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['dayofweek'] = df['date'].dt.dayofweek  # 요일 추가 (0: 월요일, 6: 일요일)
        
        # 계절 특성 추가 (1:봄, 2:여름, 3:가을, 4:겨울)
        df['season'] = df['month'].apply(lambda x: 1 if x in [3,4,5] else 2 if x in [6,7,8] else 3 if x in [9,10,11] else 4)
        
        # 가격 관련 특성 추가
        df['price_ma3'] = df[crop_name].rolling(window=3, min_periods=1).mean()  # 3일 이동평균
        df['price_ma7'] = df[crop_name].rolling(window=7, min_periods=1).mean()  # 7일 이동평균
        df['price_ma30'] = df[crop_name].rolling(window=30, min_periods=1).mean()  # 30일 이동평균
        df['price_std7'] = df[crop_name].rolling(window=7, min_periods=1).std()  # 7일 표준편차
        
        # 가격 변화율 추가
        df['price_change'] = df[crop_name].pct_change()
        df['price_change_ma7'] = df['price_change'].rolling(window=7, min_periods=1).mean()
        
        # 결측치 처리
        df = df.ffill().bfill()
        
        # 특성 선택
        features = [
            'month', 'day', 'dayofweek', 'season',
            'price_ma3', 'price_ma7', 'price_ma30',
            'price_std7', 'price_change', 'price_change_ma7'
        ]
        
        X = df[features]
        y = df[crop_name]
        
        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 특성 스케일링
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 모델 학습
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # 예측 및 평가
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        def predict_prices(weather_data=None):
            try:
                predictions = {
                    'current': {},
                    'tomorrow': {},
                    'weekly': []
                }
                
                # 현재 날짜 기준으로 예측
                current_date = datetime.now()
                
                # 데이터를 날짜 기준으로 정렬하고 가장 최근 데이터 사용
                df_sorted = df.sort_values('date', ascending=False)
                latest_price = df_sorted[crop_name].iloc[0]
                
                def prepare_prediction_data(target_date):
                    new_data = pd.DataFrame({
                        'month': [target_date.month],
                        'day': [target_date.day],
                        'dayofweek': [target_date.weekday()],
                        'season': [1 if target_date.month in [3,4,5] else 2 if target_date.month in [6,7,8] 
                                 else 3 if target_date.month in [9,10,11] else 4],
                        'price_ma3': [latest_price],
                        'price_ma7': [latest_price],
                        'price_ma30': [latest_price],
                        'price_std7': [df_sorted[crop_name].head(7).std()],
                        'price_change': [0],
                        'price_change_ma7': [0]
                    })
                    return scaler.transform(new_data)
                
                # 현재 가격 예측
                current_data = prepare_prediction_data(current_date)
                current_price = model.predict(current_data)[0]
                predictions['current'] = {
                    'price': round(current_price, 2),
                    'r2_score': round(r2, 4)
                }
                
                # 내일 가격 예측
                tomorrow_date = current_date + timedelta(days=1)
                tomorrow_data = prepare_prediction_data(tomorrow_date)
                tomorrow_price = model.predict(tomorrow_data)[0]
                predictions['tomorrow'] = {
                    'price': round(tomorrow_price, 2),
                    'r2_score': round(r2, 4)
                }
                
                # 주간 예측
                for i in range(2, 7):
                    future_date = current_date + timedelta(days=i)
                    future_data = prepare_prediction_data(future_date)
                    future_price = model.predict(future_data)[0]
                    predictions['weekly'].append({
                        'price': round(future_price, 2),
                        'r2_score': round(r2, 4)
                    })
                
                return predictions
                
            except Exception as e:
                print(f"예측 중 오류 발생: {str(e)}")
                return {"error": str(e)}
        
        return predict_prices
        
    except Exception as e:
        print(f"모델 생성 중 오류 발생: {e}")
        return None

# 각 작물별 예측 함수 생성
predict_prices_dict = {
    'apple': create_price_predictor('apple'),
    'broccoli': create_price_predictor('broccoli'),
    'cabbage': create_price_predictor('cabbage'),
    'carrot': create_price_predictor('carrot'),
    'cucumber': create_price_predictor('cucumber'),
    'onion': create_price_predictor('onion'),
    'potato': create_price_predictor('potato'),
    'spinach': create_price_predictor('spinach'),
    'strawberry': create_price_predictor('strawberry'),
    'tomato': create_price_predictor('tomato')
}

def predict_prices(crop_name, weather_data=None):
    """
    작물 이름을 받아서 해당 작물의 가격을 예측하는 함수
    """
    if crop_name not in predict_prices_dict:
        return {"error": f"지원하지 않는 작물입니다: {crop_name}"}
    
    predictor = predict_prices_dict[crop_name]
    if predictor is None:
        return {"error": f"예측 모델을 생성할 수 없습니다: {crop_name}"}
    
    return predictor(weather_data)

if __name__ == "__main__":
    # 각 작물에 대한 예측 테스트
    for crop_name in predict_prices_dict.keys():
        try:
            print(f"\n=== {crop_name} 가격 예측 결과 ===")
            predictions = predict_prices(crop_name)
            if "error" not in predictions:
                print("\n현재 예측 가격:")
                print(f"가격: {predictions['current']['price']:,.0f}원")
                print(f"정확도: {predictions['current']['r2_score']:.2%}")
                
                print("\n내일 예측 가격:")
                print(f"가격: {predictions['tomorrow']['price']:,.0f}원")
                print(f"정확도: {predictions['tomorrow']['r2_score']:.2%}")
                
                print("\n주간 예측 가격:")
                for i, daily in enumerate(predictions['weekly'], 1):
                    print(f"{i+1}일 후: {daily['price']:,.0f}원 (정확도: {daily['r2_score']:.2%})")
            else:
                print(f"오류 발생: {predictions['error']}")
                
        except Exception as e:
            print(f"{crop_name} 예측 중 오류 발생: {str(e)}")
