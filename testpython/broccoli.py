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

try:
    # 현재 파일의 절대 경로를 기준으로 CSV 파일 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(os.path.dirname(current_dir), 'testdata', 'Total_v2.csv')
    
    # CSV 파일 읽기
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    # 가격에서 쉼표 제거하고 숫자로 변환
    df['broccoli'] = df['broccoli'].astype(str).str.replace(',', '').astype(float)

    # 결측치가 있는 행(가격이 0인 행) 제거
    df = df[df['broccoli'] != 0]

    # 날짜 특성 추가
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['dayofweek'] = df['date'].dt.dayofweek  # 요일 추가 (0: 월요일, 6: 일요일)
    
    # 계절 특성 추가 (1:봄, 2:여름, 3:가을, 4:겨울)
    df['season'] = df['month'].apply(lambda x: 1 if x in [3,4,5] else 2 if x in [6,7,8] else 3 if x in [9,10,11] else 4)
    
    # 가격 관련 특성 추가
    df['price_ma3'] = df['broccoli'].rolling(window=3, min_periods=1).mean()  # 3일 이동평균
    df['price_ma7'] = df['broccoli'].rolling(window=7, min_periods=1).mean()  # 7일 이동평균
    df['price_ma30'] = df['broccoli'].rolling(window=30, min_periods=1).mean()  # 30일 이동평균
    df['price_std7'] = df['broccoli'].rolling(window=7, min_periods=1).std()  # 7일 표준편차
    
    # 가격 변화율 추가
    df['price_change'] = df['broccoli'].pct_change()
    df['price_change_ma7'] = df['price_change'].rolling(window=7, min_periods=1).mean()
    
    # 날씨 특성 추가
    df['avg_temp'] = df['avg temp']
    df['max_temp'] = df['max temp']
    df['min_temp'] = df['min temp']
    df['rainFall'] = df['rainFall']
    
    # 결측치 처리
    df = df.ffill().bfill()
    
    # 특성 선택
    features = [
        'month', 'day', 'dayofweek', 'season',
        'avg_temp', 'max_temp', 'min_temp', 'rainFall',
        'price_ma3', 'price_ma7', 'price_ma30',
        'price_std7', 'price_change', 'price_change_ma7'
    ]
    
    X = df[features]
    y = df['broccoli']
    
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
    
    print("\n브로콜리(8kg) 가격 예측 모델 평가:")
    print(f'R2 점수: {r2:.4f}')
    print(f'RMSE: {rmse:.2f}')
    
    # 특성 중요도 분석
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    })
    feature_importance = feature_importance.sort_values('importance', ascending=False)
    
    print("\n특성 중요도:")
    for idx, row in feature_importance.iterrows():
        print(f"{row['feature']}: {row['importance']:.4f}")
    
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
            latest_price = df_sorted['broccoli'].iloc[0]
            latest_weather = {
                'avg_temp': df_sorted['avg_temp'].iloc[0],
                'max_temp': df_sorted['max_temp'].iloc[0],
                'min_temp': df_sorted['min_temp'].iloc[0],
                'rainFall': df_sorted['rainFall'].iloc[0]
            }
            
            def prepare_prediction_data(target_date, weather=None):
                if weather is None:
                    weather = latest_weather
                    
                new_data = pd.DataFrame({
                    'month': [target_date.month],
                    'day': [target_date.day],
                    'dayofweek': [target_date.weekday()],
                    'season': [1 if target_date.month in [3,4,5] else 2 if target_date.month in [6,7,8] 
                             else 3 if target_date.month in [9,10,11] else 4],
                    'avg_temp': [weather['avg_temp']],
                    'max_temp': [weather['max_temp']],
                    'min_temp': [weather['min_temp']],
                    'rainFall': [weather['rainFall']],
                    'price_ma3': [latest_price],
                    'price_ma7': [latest_price],
                    'price_ma30': [latest_price],
                    'price_std7': [df_sorted['broccoli'].head(7).std()],
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
    
    if __name__ == "__main__":
        try:
            # 예측 수행
            predictions = predict_prices()
            
            # 결과 출력
            print("\n=== 브로콜리(8kg) 가격 예측 결과 ===")
            print("\n현재 예측 가격:")
            print(f"가격: {predictions['current']['price']:,.0f}원")
            print(f"정확도: {predictions['current']['r2_score']:.2%}")
            
            print("\n내일 예측 가격:")
            print(f"가격: {predictions['tomorrow']['price']:,.0f}원")
            print(f"정확도: {predictions['tomorrow']['r2_score']:.2%}")
            
            print("\n주간 예측 가격:")
            for i, daily in enumerate(predictions['weekly'], 1):
                print(f"{i+1}일 후: {daily['price']:,.0f}원 (정확도: {daily['r2_score']:.2%})")
            
            # JSON 형식으로도 출력
            print("\nJSON 형식 출력:")
            print(json.dumps(predictions, indent=2))
            
        except Exception as e:
            error_msg = {"error": str(e)}
            print(json.dumps(error_msg), file=sys.stderr)
            sys.exit(1)

except Exception as e:
    print(f"오류 발생: {e}") 