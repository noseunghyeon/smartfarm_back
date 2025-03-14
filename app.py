from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status, Request,Response
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import jwt
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv
import pandas as pd
import uvicorn
import subprocess
import json
from enum import Enum
import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import secrets
import bcrypt
from fastapi.responses import JSONResponse
from jose import JWTError
from fastapi.responses import Response
import httpx
from test import get_price_data
import threading
import sys
from backend import CommentCreate, CommentUpdate
import random
from routes.youtube import router as youtube_router
from chatbot import process_query, ChatMessage, ChatRequest, ChatCandidate, ChatResponse
from routes.Crawler import crawler_endpoint


# Load environment variables
load_dotenv()

# 도시 매핑 정의
KOREAN_CITIES = {
    "서울": "Seoul",
    "부산": "Busan",
    "대구": "Daegu",
    "인천": "Incheon",
    "광주": "Gwangju",
    "대전": "Daejeon",
    "울산": "Ulsan",
    "제주": "Jeju"
}

# Backend API URL
BACKEND_URL = "http://localhost:8080"

def run_backend():
    """Run the backend server"""
    try:
        uvicorn.run("backend:app", host="0.0.0.0", port=8080, reload=False)
    except Exception as e:
        print(f"Backend server error: {e}")
        sys.exit(1)

# Run backend server in a separate thread
backend_thread = threading.Thread(target=run_backend, daemon=True)
backend_thread.start()

from test import get_price_data, get_satellite_data

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# 데이터베이스 설정
load_dotenv()

# PostgreSQL 연결 문자열 구성
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
JWT_SECRET = os.getenv("JWT_SECRET")

if not all([DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT, JWT_SECRET]):
    raise ValueError("필수 환경 변수가 설정되지 않았습니다.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# JWT 설정
SECRET_KEY = JWT_SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 모델 정의
class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(BaseModel):
    email: str
    password: str
    birth_date: Optional[str] = None

# 인증 관련 함수들
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401)

@app.get("/")
async def root():
    return {"message": "농산물 가격 정보 API"}

@app.get("/cities")
async def get_cities():
    """사용 가능한 도시 목록을 반환합니다."""
    return {
        "success": True,
        "data": {
            "cities": list(KOREAN_CITIES.keys()),
            "mapping": KOREAN_CITIES
        },
        "message": "도시 목록을 성공적으로 가져왔습니다"
    }

@app.get("/weather")
async def get_weather(city: str):
    try:
        if not city:
            raise ValueError("도시명이 입력되지 않았습니다")
            
        if city not in KOREAN_CITIES and city not in KOREAN_CITIES.values():
            raise ValueError("지원하지 않는 도시입니다")
            
        from utils.apiUrl import fetchWeatherData
        weather_data = await fetchWeatherData(city)
        
        return {
            "success": True,
            "data": weather_data,
            "message": "날씨 데이터를 성공적으로 가져왔습니다"
        }
    except Exception as e:
        print(f"Weather API Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "날씨 데이터를 가져오는데 실패했습니다"
        }

@app.post("/predict")
async def predict_disease(file: UploadFile = File(...), crop_type: str = "kiwi"):
    try:
        async with httpx.AsyncClient() as client:
            form_data = {"file": await file.read()}
            files = {"file": (file.filename, form_data["file"], file.content_type)}
            
            # 작물 유형에 따라 다른 엔드포인트 호출
            if crop_type == "kiwi":
                endpoint = "/kiwi_predict"
            elif crop_type == "chamoe":
                endpoint = "/chamoe_predict"
            elif crop_type == "plant":  # 식물 분류 엔드포인트 추가
                endpoint = "/plant_predict"
            else:
                raise HTTPException(status_code=400, detail="지원하지 않는 작물 유형입니다")
            
            response = await client.post(
                f"http://localhost:8080{endpoint}",
                files=files
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                return {
                    "success": False,
                    "error": "이미지 분석 실패",
                    "message": "이미지 분석 중 오류가 발생했습니다"
                }
                
    except Exception as e:
        print(f"Prediction Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "이미지 분석 중 오류가 발생했습니다"
        }

@app.get("/predictions/{crop}/{city}")
async def get_predictions(crop: str, city: str):
    try:
        from utils.apiUrl import fetchWeatherData
        
        # 작물에 따른 예측 모듈 선택
        if crop == "cabbage":
            from testpython.cabbage2 import predict_prices
        elif crop == "apple":
            from testpython.appleprice import predict_prices
        elif crop == "broccoli":
            from testpython.broccoli import predict_prices
        elif crop == "carrot":
            from testpython.carrot import predict_prices
        elif crop == "onion":
            from testpython.onion2 import predict_prices
        elif crop == "potato":
            from testpython.potato2 import predict_prices
        elif crop == "cucumber":
            from testpython.cucumber2 import predict_prices
        elif crop == "tomato":
            from testpython.tomato2 import predict_prices
        elif crop == "spinach":
            from testpython.spinach2 import predict_prices
        elif crop == "strawberry":
            from testpython.strawberry import predict_prices
        else:
            raise ValueError("지원하지 않는 작물입니다")
        
        weather_data = await fetchWeatherData(city)
        predictions = predict_prices(weather_data)
        
        if 'error' in predictions:
            raise Exception(predictions['error'])
            
        return {
            "predictions": predictions,
            "weather_data": weather_data['raw']
        }
    except Exception as e:
        print(f"Error in predictions: {str(e)}")
        return {"error": str(e)}

@app.get("/api/satellite")
async def get_satellite():
    """한반도 위성 구름 이미지 정보를 가져옵니다."""
    try:
        result = get_satellite_data()
        if result is None:
            raise HTTPException(status_code=500, detail="위성 데이터를 가져오는데 실패했습니다")
        return {
            "success": True,
            "data": result,
            "message": "위성 이미지 데이터를 성공적으로 가져왔습니다"
        }
    except Exception as e:
        print(f"Satellite API Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "위성 이미지 데이터를 가져오는데 실패했습니다"
        }

@app.get("/api/price")
async def get_price():
    try:
        result = get_price_data()
        if result is None:
            raise HTTPException(status_code=500, detail="데이터를 가져오는데 실패했습니다")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/auth/register")
async def register(user: UserCreate):
    try:
        db = SessionLocal()
        
        # 이메일 중복 확인
        check_query = text("SELECT user_id FROM auth WHERE email = :email")
        existing_user = db.execute(check_query, {"email": user.email}).scalar()
        
        if existing_user:
            return {
                "success": False,
                "message": "Email already exists"
            }
        
        # 비밀번호 해시화
        hashed_password = bcrypt.hashpw(
            user.password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # 새 사용자 추가
        query = text("""
            INSERT INTO auth (email, password, birth_date, created_at)
            VALUES (:email, :password, :birth_date, NOW())
            RETURNING user_id, email, birth_date, created_at
        """)
        
        result = db.execute(
            query,
            {
                "email": user.email,
                "password": hashed_password,
                "birth_date": user.birth_date
            }
        )
        db.commit()
        
        new_user = result.fetchone()
        
        return {
            "success": True,
            "data": {
                "user": {
                    "user_id": new_user.user_id,
                    "email": new_user.email,
                    "birth_date": new_user.birth_date.strftime('%Y-%m-%d') if new_user.birth_date else None,
                    "created_at": new_user.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": str(e)
        }
    finally:
        db.close()

# Pydantic 모델 정의
class LoginData(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.post("/auth/login")
async def login(login_data: LoginData):
    try:
        db = SessionLocal()
        
        # 사용자 정보 조회
        query = text("""
            SELECT user_id, email, password, birth_date, created_at 
            FROM auth 
            WHERE email = :email
        """)
        result = db.execute(query, {"email": login_data.email})
        user = result.fetchone()
        
        if not user:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "User not found"
                },
                status_code=404
            )
            
        # 비밀번호 확인
        if not bcrypt.checkpw(
            login_data.password.encode('utf-8'),
            user.password.encode('utf-8')
        ):
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Incorrect password"
                },
                status_code=401
            )
        
        # 토큰 생성
        token_data = {
            "sub": login_data.email,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        access_token = create_access_token(token_data)
        
        return JSONResponse(
            content={
                "success": True,
                "data": {
                    "user": {
                        "user_id": user.user_id,
                        "email": user.email,
                        "birth_date": user.birth_date.strftime('%Y-%m-%d') if user.birth_date else None,
                        "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    },
                    "access_token": access_token,
                    "token_type": "bearer"
                }
            },
            status_code=200
        )
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "message": str(e)
            },
            status_code=400
        )
    finally:
        db.close()


# 커뮤니티 타입 열거형 정의
class CommunityType(str, Enum):
    GARDENING = "gardening"
    MARKETPLACE = "marketplace"
    FREEBOARD = "freeboard"

# Pydantic 모델 수정
class PostCreate(BaseModel):
    title: str
    content: str
    category: str
    community_type: CommunityType

@app.post("/api/write/create")
async def create_write_post(post: PostCreate, current_user: str = Depends(get_current_user)):
    try:
        db = SessionLocal()
        current_time = datetime.now()
        
        # auth 테이블에서 user_id 조회
        user_query = text("SELECT user_id FROM auth WHERE email = :email")
        user_result = db.execute(user_query, {"email": current_user})
        user_id = user_result.scalar()
        
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 게시글 작성 쿼리
        query = text("""
            INSERT INTO write (user_id, title, content, date, category, community_type)
            VALUES (:user_id, :title, :content, :date, :category, :community_type)
            RETURNING post_id, user_id, title, content, date, category, community_type
        """)
        
        result = db.execute(
            query,
            {
                "user_id": user_id,
                "title": post.title,
                "content": post.content,
                "date": current_time,
                "category": post.category,
                "community_type": post.community_type.value
            }
        )
        db.commit()
        
        new_post = result.fetchone()
        
        return {
            "success": True,
            "data": {
                "post_id": new_post.post_id,
                "user_id": new_post.user_id,
                "title": new_post.title,
                "content": new_post.content,
                "date": new_post.date,
                "category": new_post.category,
                "community_type": new_post.community_type
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 댓글 관련 API 엔드포인트
@app.get("/api/comments/user")
async def get_my_comments(request: Request):
    try:
        # 1. 토큰 추출
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise HTTPException(status_code=401, detail="인증 헤더가 없습니다")
            
        logger.info(f"[App] 수신된 인증 헤더: {auth_header}")
        
        # 2. backend로 요청 전달
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'http://localhost:8080/api/comments/user',
                headers={'Authorization': auth_header}
            )
            
            logger.info(f"[App] Backend 응답 상태 코드: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"[App] Backend 응답 에러: {response.text}")
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            
            return response.json()
            
    except Exception as e:
        logger.error(f"[App] 에러 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/comments/{post_id}")
async def get_comments(post_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/api/comments/{post_id}")
        return response.json()

@app.post("/api/comments")
async def create_comment(comment: CommentCreate):
    try:
        logger.info(f"Received comment data: {comment.dict()}")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_URL}/api/comments", json=comment.dict())
            if response.status_code != 200:
                logger.error(f"Backend error: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
            return response.json()
    except Exception as e:
        logger.error(f"Error creating comment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/comments/{comment_id}")
async def update_comment(
    comment_id: int, 
    comment_update: CommentUpdate,
    current_user: str = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logging.info(f"댓글 수정 요청: comment_id={comment_id}, user={current_user}")
            
            # 프론트엔드 데이터 형식에 맞게 변환
            request_data = {
                "commentId": comment_id,
                "content": comment_update.content,
                "userEmail": current_user
            }
            
            logging.info(f"요청 데이터: {request_data}")
            
            response = await client.put(
                f"{BACKEND_URL}/api/comments/{comment_id}",
                json=request_data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {token}"
                }
            )
            
            logging.info(f"백엔드 응답: {response.status_code} - {response.text}")
            
            if response.status_code == 401:
                logging.error("인증 오류: 토큰이 만료되었거나 유효하지 않습니다")
                raise HTTPException(
                    status_code=401,
                    detail="로그인이 필요하거나 인증이 만료되었습니다. 다시 로그인해주세요."
                )
            
            if response.status_code != 200:
                logging.error(f"백엔드 서버 오류: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            return response.json()
    except httpx.RequestError as e:
        logging.error(f"백엔드 서버 연결 오류: {str(e)}")
        raise HTTPException(status_code=503, detail="백엔드 서버에 연결할 수 없습니다.")
    except Exception as e:
        logging.error(f"댓글 수정 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: str = Depends(get_current_user)
):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BACKEND_URL}/api/comments/{comment_id}",
            params={"user_email": current_user}
        )
        return response.json()

@app.get("/api/test-db")
async def test_db():
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT NOW()"))
        return {"success": True, "timestamp": result.scalar()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/sales")
async def get_sales():
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT * FROM sales_data_2024"))
        # 컬럼 이름을 키로 사용하여 딕셔너리 생성
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result]
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/top10")
async def get_top10():
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT * FROM top_10_sales"))
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result]
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/get_text")
async def get_text(request: Request):
    try:
        # 요청 본문 읽기
        body = await request.json()
        
        # Python 프로세스 실행
        process = subprocess.Popen(
            ["python", "app.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 데이터 전송 및 결과 받기
        stdout, stderr = process.communicate(input=json.dumps(body))
        
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Python Error: {stderr}")
            
        try:
            prediction = json.loads(stdout)
            return prediction
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to parse Python output")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/market")
async def get_market():
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT * FROM sales_data_2024"))
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result]
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.on_event("shutdown")
async def shutdown_event():
    # PostgreSQL pool 정리
    engine.dispose()

# 게시글 수정을 위한 모델
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    community_type: Optional[CommunityType] = None

# 댓글 수정을 위한 모델
class CommentUpdate(BaseModel):
    content: str

# 게시글 수정
@app.put("/api/posts/{post_id}")
async def update_post(
    post_id: int, 
    post_update: PostUpdate, 
    current_user: str = Depends(get_current_user)
):
    try:
        db = SessionLocal()
        
        # 게시글 작성자 확인
        check_query = text("""
            SELECT w.user_id, a.email 
            FROM write w 
            JOIN auth a ON w.user_id = a.user_id 
            WHERE w.post_id = :post_id
        """)
        result = db.execute(check_query, {"post_id": post_id})
        post = result.fetchone()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.email != current_user:
            raise HTTPException(status_code=403, detail="Not authorized to update this post")
        
        # 수정할 필드 구성
        update_fields = {}
        if post_update.title is not None:
            update_fields["title"] = post_update.title
        if post_update.content is not None:
            update_fields["content"] = post_update.content
        if post_update.category is not None:
            update_fields["category"] = post_update.category
        if post_update.community_type is not None:
            update_fields["community_type"] = post_update.community_type.value
        
        if update_fields:
            # 게시글 수정 쿼리
            update_query = text(f"""
                UPDATE write 
                SET {', '.join(f"{k} = :{k}" for k in update_fields.keys())}
                WHERE post_id = :post_id
                RETURNING *
            """)
            
            result = db.execute(update_query, {**update_fields, "post_id": post_id})
            db.commit()
            updated_post = result.fetchone()
            
            return {"success": True, "data": dict(updated_post)}
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# 게시글 삭제
@app.delete("/api/write/{post_id}")
async def delete_post(
    post_id: int, 
    current_user: str = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        logging.info(f"게시글 삭제 요청: post_id={post_id}, user={current_user}")
        
        db = SessionLocal()
        
        # 게시글 작성자 확인
        check_query = text("""
            SELECT w.user_id, a.email 
            FROM write w 
            JOIN auth a ON w.user_id = a.user_id 
            WHERE w.post_id = :post_id
        """)
        result = db.execute(check_query, {"post_id": post_id})
        post = result.fetchone()
        
        if not post:
            logging.error(f"게시글을 찾을 수 없음: post_id={post_id}")
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
            
        if post.email != current_user:
            logging.error(f"권한 없음: post_id={post_id}, user={current_user}")
            raise HTTPException(status_code=403, detail="게시글을 삭제할 권한이 없습니다")
        
        # 연관된 댓글 삭제
        db.execute(text("DELETE FROM comments WHERE post_id = :post_id"), {"post_id": post_id})
        
        # 게시글 삭제
        db.execute(text("DELETE FROM write WHERE post_id = :post_id"), {"post_id": post_id})
        db.commit()
        
        logging.info(f"게시글 삭제 완료: post_id={post_id}")
        return {"success": True, "message": "게시글이 성공적으로 삭제되었습니다"}
        
    except Exception as e:
        db.rollback()
        logging.error(f"게시글 삭제 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# 이메일 설정
email_conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.naver.com"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True
)

# 비밀번호 재설정 모델
class PasswordReset(BaseModel):
    email: EmailStr
    token: str
    new_password: str

# 비밀번호 변경 모델
class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# 회원 탈퇴
@app.delete("/auth/user")
async def delete_user(current_user: str = Depends(get_current_user)):
    try:
        db = SessionLocal()
        
        # 사용자 ID 조회
        user_query = text("SELECT user_id FROM auth WHERE email = :email")
        user_result = db.execute(user_query, {"email": current_user})
        user_id = user_result.scalar()
        
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 사용자의 댓글 삭제
        db.execute(
            text("DELETE FROM comments WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        
        # 사용자의 게시글 삭제
        db.execute(
            text("DELETE FROM write WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        
        # 사용자 계정 삭제
        db.execute(
            text("DELETE FROM auth WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        
        db.commit()
        return {"success": True, "message": "User account deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# 인증 코드 저장을 위한 임시 저장소
verification_codes = {}

@app.post("/auth/verify-email")
async def send_verification_email(email: EmailStr):
    try:
        # 6자리 인증 코드 생성
        verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # 인증 코드 저장 (5분 동안 유효)
        verification_codes[email] = {
            'code': verification_code,
            'expires_at': datetime.utcnow() + timedelta(minutes=5)
        }
        
        # 이메일 발송
        message = MessageSchema(
            subject="이메일 인증",
            recipients=[email],
            body=f"""
            안녕하세요! AniFarm 회원가입을 위한 인증 코드입니다:
            
            인증 코드: {verification_code}
            
            이 코드는 3분 동안만 유효합니다.
            """,
            subtype="plain"
        )
        
        try:
            fastmail = FastMail(email_conf)
            await fastmail.send_message(message)
            return {"success": True, "message": "인증 코드가 발송되었습니다."}
        except Exception as email_error:
            print(f"이메일 발송 상세 오류: {str(email_error)}")
            print(f"오류 타입: {type(email_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"이메일 발송 중 오류가 발생했습니다: {str(email_error)}"
            )
        
    except Exception as e:
        print(f"기타 오류: {str(e)}")
        print(f"오류 타입: {type(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"처리 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/auth/verify-code")
async def verify_code(email: EmailStr, code: str):
    if email not in verification_codes:
        raise HTTPException(status_code=400, detail="인증 코드를 찾을 수 없습니다.")
        
    stored_data = verification_codes[email]
    if datetime.utcnow() > stored_data['expires_at']:
        del verification_codes[email]
        raise HTTPException(status_code=400, detail="인증 코드가 만료되었습니다.")
        
    if code != stored_data['code']:
        raise HTTPException(status_code=400, detail="잘못된 인증 코드입니다.")
        
    # 인증 성공 시 코드 삭제
    del verification_codes[email]
    return {"success": True, "message": "이메일이 성공적으로 인증되었습니다."}

@app.get("/auth/verify-email/{token}")
async def verify_email_token(token: str):
    try:
        # 토큰 검증
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        email = payload["email"]
        
        # 여기서 필요한 경우 사용자의 이메일 인증 상태를 업데이트할 수 있습니다
        # 예: Auth 테이블에 verified 필드를 추가하여 업데이트
        
        return {"message": "이메일이 성공적으로 인증되었습니다."}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=400,
            detail="인증 링크가 만료되었습니다. 다시 인증 이메일을 요청해주세요."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=400,
            detail="유효하지 않은 인증 링크입니다."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"인증 처리 중 오류가 발생했습니다: {str(e)}"
        )

# 비밀번호 재설정 요청
@app.post("/auth/reset-password-request")
async def request_password_reset(email: EmailStr):
    try:
        db = SessionLocal()
        
        # 사용자 존재 확인
        user_query = text("SELECT user_id FROM auth WHERE email = :email")
        user_result = db.execute(user_query, {"email": email})
        if not user_result.scalar():
            raise HTTPException(status_code=404, detail="User not found")
        
        # 재설정 토큰 생성
        token = secrets.token_urlsafe(32)
        
        # 토큰 저장
        query = text("""
            INSERT INTO password_resets (email, token, created_at)
            VALUES (:email, :token, NOW())
        """)
        db.execute(query, {"email": email, "token": token})
        db.commit()
        
        # 이메일 발송
        message = MessageSchema(
            subject="비밀번호 재설정",
            recipients=[email],
            body=f"""
            안녕하세요!
            아래 링크를 클릭하여 비밀번호를 재설정해주세요:
            http://localhost:3000/reset-password?token={token}
            """
        )
        
        fastmail = FastMail(email_conf)
        await fastmail.send_message(message)
        
        return {"success": True, "message": "Password reset email sent"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# 비밀번호 재설정
@app.post("/auth/reset-password")
async def reset_password(reset_data: PasswordReset):
    try:
        db = SessionLocal()
        
        # 토큰 유효성 검사
        token_query = text("""
            SELECT email FROM password_resets 
            WHERE token = :token AND created_at > NOW() - INTERVAL '2 hour'
            AND used = false
        """)
        result = db.execute(token_query, {"token": reset_data.token})
        stored_email = result.scalar()
        
        if not stored_email or stored_email != reset_data.email:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        # 비밀번호 해시화
        hashed_password = bcrypt.hashpw(
            reset_data.new_password.encode('utf-8'), 
            bcrypt.gensalt()
        )
        
        # 비밀번호 업데이트
        update_query = text("""
            UPDATE auth SET password = :password 
            WHERE email = :email
        """)
        db.execute(update_query, {
            "password": hashed_password.decode('utf-8'),
            "email": reset_data.email
        })
        
        # 토큰 사용 완료 표시
        db.execute(
            text("UPDATE password_resets SET used = true WHERE token = :token"),
            {"token": reset_data.token}
        )
        
        db.commit()
        return {"success": True, "message": "Password reset successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# 비밀번호 수정 모델
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

@app.post("/auth/update-password")
async def update_password(
    password_data: PasswordUpdate,
    current_user: str = Depends(get_current_user)
):
    try:
        db = SessionLocal()
        
        # 현재 사용자의 비밀번호 확인
        query = text("SELECT password FROM auth WHERE email = :email")
        result = db.execute(query, {"email": current_user})
        stored_password = result.scalar()
        
        if not stored_password:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # 현재 비밀번호 확인
        if not bcrypt.checkpw(
            password_data.current_password.encode('utf-8'),
            stored_password.encode('utf-8')
        ):
            return {
                "success": False,
                "message": "Current password is incorrect"
            }
        
        # 새 비밀번호 해시화
        new_hashed_password = bcrypt.hashpw(
            password_data.new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # 비밀번호 업데이트
        update_query = text("""
            UPDATE auth 
            SET password = :password 
            WHERE email = :email
            RETURNING user_id, email, birth_date, created_at
        """)
        
        result = db.execute(
            update_query,
            {
                "password": new_hashed_password,
                "email": current_user
            }
        )
        db.commit()
        
        updated_user = result.fetchone()
        
        return {
            "success": True,
            "data": {
                "user": {
                    "user_id": updated_user.user_id,
                    "email": updated_user.email,
                    "birth_date": updated_user.birth_date.strftime('%Y-%m-%d') if updated_user.birth_date else None,
                    "created_at": updated_user.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            },
            "message": "Password updated successfully"
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": str(e)
        }
    finally:
        db.close()

@app.get("/api/write/community/{community_type}")
async def get_community_posts(community_type: str):
    try:
        db = SessionLocal()
        result = db.execute(
            text("""
                SELECT w.*, u.email 
                FROM write w 
                JOIN auth u ON w.user_id = u.user_id 
                WHERE w.community_type = :community_type 
                ORDER BY w.date DESC
            """),
            {"community_type": community_type}
        )
        posts = result.fetchall()
        
        # 데이터 변환 로직 수정
        posts_data = []
        for post in posts:
            post_dict = {
                "post_id": post.post_id,
                "user_id": post.user_id,
                "title": post.title,
                "content": post.content,
                "date": post.date,
                "category": post.category,
                "community_type": post.community_type,
                "email": post.email
            }
            posts_data.append(post_dict)
        
        return {
            "success": True,
            "data": posts_data
        }
    except Exception as e:
        print(f"[ERROR] 게시글 조회 중 오류 발생: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }
    finally:
        db.close()

@app.get("/api/posts/{post_id}")
async def get_post_detail(post_id: int):
    try:
        db = SessionLocal()
        result = db.execute(
            text("""
                SELECT w.*, u.email 
                FROM write w 
                JOIN auth u ON w.user_id = u.user_id 
                WHERE w.post_id = :post_id
            """),
            {"post_id": post_id}
        )
        post = result.fetchone()
        
        if not post:
            return {
                "success": False,
                "message": "게시글을 찾을 수 없습니다."
            }
        
        # 데이터 변환
        post_data = {
            "post_id": post.post_id,
            "user_id": post.user_id,
            "title": post.title,
            "content": post.content,
            "date": post.date,
            "category": post.category,
            "community_type": post.community_type,
            "email": post.email
        }
        
        return {
            "success": True,
            "data": post_data
        }
    except Exception as e:
        print(f"[ERROR] 게시글 상세 조회 중 오류 발생: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }
    finally:
        db.close()

@app.get("/auth/user")
async def get_user_info(current_user: str = Depends(get_current_user)):
    try:
        db = SessionLocal()
        
        # 사용자 정보 조회
        query = text("""
            SELECT 
                user_id, 
                email, 
                TO_CHAR(birth_date, 'YYYY-MM-DD') as birth_date,
                TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') as created_at
            FROM auth 
            WHERE email = :email
        """)
        result = db.execute(query, {"email": current_user})
        user = result.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        return {
            "success": True,
            "data": {
                "user_id": user.user_id,
                "email": user.email,
                "birth_date": user.birth_date,
                "created_at": user.created_at
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# YouTube 라우터 포함
app.include_router(youtube_router)

# 내 게시글 조회 엔드포인트
@app.get("/api/write/user")  # URL 변경
async def get_my_posts(current_user: str = Depends(get_current_user)):
    try:
        db = SessionLocal()
        
        # 사용자 ID 조회
        user_query = text("SELECT user_id FROM auth WHERE email = :email")
        user_result = db.execute(user_query, {"email": current_user})
        user_id = user_result.scalar()
        
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 사용자의 게시글 조회
        posts_query = text("""
            SELECT w.*, a.email 
            FROM write w 
            JOIN auth a ON w.user_id = a.user_id 
            WHERE w.user_id = :user_id 
            ORDER BY w.date DESC
        """)
        
        result = db.execute(posts_query, {"user_id": user_id})
        posts = result.fetchall()
        
        posts_data = []
        for post in posts:
            post_dict = {
                "post_id": post.post_id,
                "title": post.title,
                "content": post.content,
                "date": post.date,
                "category": post.category,
                "community_type": post.community_type,
                "email": post.email
            }
            posts_data.append(post_dict)
        
        return {
            "success": True,
            "data": posts_data,
            "message": "게시글 조회 성공"
        }
        
    except Exception as e:
        logger.error(f"게시글 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# Crawler 라우터 포함
app.include_router(crawler_endpoint.router, prefix="/api/crawler")


if __name__ == "__main__":
    print("Main Server is running on port 8000")
    
    try:
        # 메인 앱 실행
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        pass