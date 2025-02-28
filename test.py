import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv


def get_price_data():
    # .env 파일 로드
    load_dotenv()
    
    # 오늘 날짜 가져오기 (YYYY-MM-DD 형식)
    today = datetime.now().strftime('%Y-%m-%d')
    
    # API 엔드포인트 URL
    url = "http://www.kamis.or.kr/service/price/xml.do"
    
    # API 요청 파라미터
    params = {
        "action": "dailyPriceByCategoryList",
        "p_product_cls_code": "02",
        "p_country_code": "1101",
        "p_regday": today,
        "p_convert_kg_yn": "N",
        "p_item_category_code": "200",
        "p_cert_key": os.getenv('KAMIS_API_KEY'),
        "p_cert_id": "5243",
        "p_returntype": "json"
    }

    try:
        # API 호출
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTP 에러 체크
        
        # JSON 응답 파싱
        data = response.json()
        
        # 데이터 반환
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"API 호출 중 오류 발생: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    get_price_data()