# 베이스 이미지 선택
FROM python:3.9

# 작업 디렉터리 설정
WORKDIR /app

# 필요한 파일 복사
COPY requirements.txt .
COPY app.py .
COPY weather.py .
COPY youtube.py .
COPY chatbot.py .
COPY image_classifier.py .
COPY growthcalendar.py .
COPY young_api.py .
COPY support.py .
COPY swagger.py .

# 디렉토리 복사
COPY utils/ ./utils/
COPY services/ ./services/
COPY Crawler/ ./Crawler/

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 컨테이너가 실행될 때 실행할 명령어
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 