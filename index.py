from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import sys
import signal
import psycopg2
from typing import Optional
from routes import weather_routes, youtube_routes

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(weather_routes.router)
app.include_router(youtube_routes.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Server is running"}

@app.post("/get_text")
async def get_text(request: Request):
    try:
        data = await request.json()
        # 여기에 기존 Python 처리 로직 구현
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 종료 시 처리를 위한 시그널 핸들러
def signal_handler(sig, frame):
    print("서버를 종료합니다...")
    # DB 연결 종료 등의 정리 작업
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000) 