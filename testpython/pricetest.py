import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_squared_error, r2_score
import sys
import json
import os

# 전역 변수로 모델과 스케일러 선언
models = {}
scores = {}
scaler = None

def init_model():
    global models, scores, scaler
    try:
        # UTF-8 인코딩으로 설정
        if sys.platform.startswith('win'):
            import locale
            locale.setlocale(locale.LC_ALL, 'Korean_Korea.UTF-8')
        
        # 현재 파일의 절대 경로를 기준으로 CSV 파일 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(os.path.dirname(current_dir), 'testdata', 'Total.csv')
        
        # CSV 파일 읽기
        df = pd.read_csv(csv_path, encoding='utf-8')

        # 결측치가 있는 행 제거
        df = df[~(df[['cabbage', 'potato', 'apple', 'onion', 'cucumber', 
                   'pepper', 'paprika', 'spinach', 'tomato', 'lettuce']] == 0).any(axis=1)]

        # 특성(X)과 타겟(y) 데이터 분리
        X = df[['avg temp', 'max temp', 'min temp', 'rainFall']]
        vegetables = ['cabbage', 'potato', 'apple', 'onion', 'cucumber', 
                      'pepper', 'paprika', 'spinach', 'tomato', 'lettuce']

        # 데이터 전처리
        scaler = RobustScaler()
        X_scaled = scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

        for veg in vegetables:
            y = df[veg]
            
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.15, random_state=42
            )
            
            model = GradientBoostingRegressor(
                n_estimators=500,
                learning_rate=0.01,
                max_depth=5,
                min_samples_split=10,
                min_samples_leaf=5,
                subsample=0.8,
                random_state=42
            )
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            models[veg] = model
            scores[veg] = {'R2': r2, 'RMSE': rmse}
        
        return True
    except Exception as e:
        print(f"모델 초기화 오류: {str(e)}")
        return False

def predict_prices(weather_data):
    try:
        if not models or not scores:
            if not init_model():
                return {"error": "모델 초기화 실패"}

        predictions = {
            'current': {},
            'tomorrow': {},
            'weekly': []
        }
        
        # 현재 가격 예측
        if isinstance(weather_data, pd.DataFrame):
            current_data = weather_data
        else:
            current_data = pd.DataFrame({
                'avg temp': [weather_data['current']['avg temp']],
                'max temp': [weather_data['current']['max temp']],
                'min temp': [weather_data['current']['min temp']],
                'rainFall': [weather_data['current']['rainFall']]
            })
        
        current_scaled = scaler.transform(current_data)
        
        for veg in models.keys():
            current_price = models[veg].predict(current_scaled)[0]
            predictions['current'][f"{veg}_price"] = round(current_price, 2)
            predictions['current'][f"{veg}_r2"] = round(scores[veg]['R2'], 4)
        
        # 내일 가격 예측
        if isinstance(weather_data, dict) and 'tomorrow' in weather_data:
            tomorrow_data = pd.DataFrame({
                'avg temp': [weather_data['tomorrow']['avg temp']],
                'max temp': [weather_data['tomorrow']['max temp']],
                'min temp': [weather_data['tomorrow']['min temp']],
                'rainFall': [weather_data['tomorrow']['rainFall']]
            })
            
            tomorrow_scaled = scaler.transform(tomorrow_data)
            
            for veg in models.keys():
                tomorrow_price = models[veg].predict(tomorrow_scaled)[0]
                predictions['tomorrow'][f"{veg}_price"] = round(tomorrow_price, 2)
                predictions['tomorrow'][f"{veg}_r2"] = round(scores[veg]['R2'], 4)
        
        # 주간 가격 예측
        if isinstance(weather_data, dict) and 'weekly' in weather_data:
            for day_data in weather_data['weekly']:
                daily_data = pd.DataFrame({
                    'avg temp': [day_data['avg temp']],
                    'max temp': [day_data['max temp']],
                    'min temp': [day_data['min temp']],
                    'rainFall': [day_data['rainFall']]
                })
                
                daily_scaled = scaler.transform(daily_data)
                
                daily_predictions = {}
                for veg in models.keys():
                    daily_price = models[veg].predict(daily_scaled)[0]
                    daily_predictions[f"{veg}_price"] = round(daily_price, 2)
                    daily_predictions[f"{veg}_r2"] = round(scores[veg]['R2'], 4)
                predictions['weekly'].append(daily_predictions)
        
        return predictions
        
    except Exception as e:
        print(f"예측 오류: {str(e)}")
        return {"error": str(e)}

# 모델 초기화
init_model()

if __name__ == "__main__":
    try:
        # 표준 입력에서 날씨 데이터 읽기
        input_data = sys.stdin.read()
        weather_data = json.loads(input_data)
        
        # 예측 수행
        predictions = predict_prices(weather_data)
        
        # JSON 형식으로 결과 출력
        print(json.dumps(predictions))
        
    except Exception as e:
        error_msg = {"error": str(e)}
        print(json.dumps(error_msg), file=sys.stderr)
        sys.exit(1)