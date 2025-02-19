import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import sys
import json
import os
from datetime import datetime

try:
    # 현재 파일의 절대 경로를 기준으로 CSV 파일 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(os.path.dirname(current_dir), 'testdata', 'Total.csv')
    
    # CSV 파일 읽기
    df = pd.read_csv(csv_path, encoding='utf-8')

    # 결측치가 있는 행(가격이 0인 행) 제거
    df = df[df['lettuce'] != 0]

    # 날짜 특성 추가
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['season'] = df['month'].apply(lambda x: 1 if x in [3,4,5] else 2 if x in [6,7,8] else 3 if x in [9,10,11] else 4)
    
    # 기온 차이 특성 추가
    df['temp_diff'] = df['max temp'] - df['min temp']
    
    # 이동평균 특성 추가
    df['price_ma7'] = df['lettuce'].rolling(window=7).mean()
    df['price_ma30'] = df['lettuce'].rolling(window=30).mean()
    
    # 특성과 타겟 분리
    features = ['avg temp', 'max temp', 'min temp', 'rainFall', 'month', 'day', 'season', 'temp_diff', 'price_ma7', 'price_ma30']
    X = df[features]
    y = df['lettuce']
    
    # 결측치 처리
    X = X.fillna(method='ffill')
    
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
    
    print("\n상추 가격 예측 모델 평가:")
    print(f'R2 점수: {r2:.4f}')
    print(f'RMSE: {rmse:.2f}')
    
    # 특성 중요도 분석
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    })
    feature_importance = feature_importance.sort_values('importance', ascending=False)
    
    print("\n특성 중요도:")
    for idx, row in feature_importance.iterrows():
        print(f"{row['feature']}: {row['importance']:.4f}")
    
    def predict_price(temp_avg, temp_max, temp_min, rainfall, month=datetime.now().month):
        season = 1 if month in [3,4,5] else 2 if month in [6,7,8] else 3 if month in [9,10,11] else 4
        temp_diff = temp_max - temp_min
        price_ma7 = df['lettuce'].mean()
        price_ma30 = df['lettuce'].mean()
        
        new_data = pd.DataFrame({
            'avg temp': [temp_avg],
            'max temp': [temp_max],
            'min temp': [temp_min],
            'rainFall': [rainfall],
            'month': [month],
            'day': [datetime.now().day],
            'season': [season],
            'temp_diff': [temp_diff],
            'price_ma7': [price_ma7],
            'price_ma30': [price_ma30]
        })
        
        new_data_scaled = scaler.transform(new_data)
        prediction = model.predict(new_data_scaled)[0]
        return max(0, prediction)
    
    def predict_prices(weather_data):
        try:
            predictions = {
                'current': {},
                'tomorrow': {},
                'weekly': []
            }
            
            if 'current' in weather_data:
                current_price = predict_price(
                    temp_avg=weather_data['current']['avg temp'],
                    temp_max=weather_data['current']['max temp'],
                    temp_min=weather_data['current']['min temp'],
                    rainfall=weather_data['current']['rainFall']
                )
                predictions['current'] = {
                    'price': round(current_price, 2),
                    'r2_score': round(r2, 4)
                }
            
            if 'tomorrow' in weather_data:
                tomorrow_price = predict_price(
                    temp_avg=weather_data['tomorrow']['avg temp'],
                    temp_max=weather_data['tomorrow']['max temp'],
                    temp_min=weather_data['tomorrow']['min temp'],
                    rainfall=weather_data['tomorrow']['rainFall']
                )
                predictions['tomorrow'] = {
                    'price': round(tomorrow_price, 2),
                    'r2_score': round(r2, 4)
                }
            
            if 'weekly' in weather_data:
                for day_weather in weather_data['weekly']:
                    daily_price = predict_price(
                        temp_avg=day_weather['avg temp'],
                        temp_max=day_weather['max temp'],
                        temp_min=day_weather['min temp'],
                        rainfall=day_weather['rainFall']
                    )
                    predictions['weekly'].append({
                        'price': round(daily_price, 2),
                        'r2_score': round(r2, 4)
                    })
            
            return predictions
            
        except Exception as e:
            return {"error": str(e)}
    
    if __name__ == "__main__":
        try:
            # 표준 입력에서 날씨 데이터 읽기
            input_data = sys.stdin.read()
            weather_data = json.loads(input_data)
            
            # 예측 수행
            predictions = predict_prices(weather_data)
            
            # 결과 출력
            print("\n=== 상추 가격 예측 결과 ===")
            print("\n현재 예측 가격:")
            print(f"가격: {predictions['current']['price']:,.0f}원")
            print(f"정확도: {predictions['current']['r2_score']:.2%}")
            
            print("\n내일 예측 가격:")
            print(f"가격: {predictions['tomorrow']['price']:,.0f}원")
            print(f"정확도: {predictions['tomorrow']['r2_score']:.2%}")
            
            print("\n주간 예측 가격:")
            for i, daily in enumerate(predictions['weekly'], 1):
                print(f"{i}일 후: {daily['price']:,.0f}원 (정확도: {daily['r2_score']:.2%})")
            
            # JSON 형식으로도 출력
            print("\nJSON 형식 출력:")
            print(json.dumps(predictions, indent=2))
            
        except Exception as e:
            error_msg = {"error": str(e)}
            print(json.dumps(error_msg), file=sys.stderr)
            sys.exit(1)

except Exception as e:
    print(f"오류 발생: {e}")