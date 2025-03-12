from fastapi import FastAPI, HTTPException, Depends, Header, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime
from typing import Optional, List, Dict
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from test import get_price_data
import logging
from fastapi.security import OAuth2PasswordBearer
import jwt
from chatbot import process_query, ChatMessage, ChatRequest, ChatCandidate, ChatResponse

# kiwi_model 관련 import 추가
import torch
import onnxruntime
import numpy as np
from torchvision import transforms
import io
from PIL import Image
import requests

app = FastAPI()

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 대화 기록 초기화
app.state.conversation_history = []

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# kiwi_model 관련 코드 추가
# 클래스 레이블 정의
CLASS_LABELS = {
    0: "잎_점무늬병",
    1: "잎_정상",
    2: "잎_총채벌레"
}

# ONNX 모델 다운로드
def download_onnx_model():
    model_path = "model.onnx"
    if not os.path.exists(model_path):
        url = "https://huggingface.co/jjiw/densenet161-onnx/resolve/main/model.onnx"
        response = requests.get(url)
        with open(model_path, "wb") as f:
            f.write(response.content)
    return model_path

# ONNX 런타임 세션 생성
model_path = download_onnx_model()
session = onnxruntime.InferenceSession(model_path)

# 이미지 전처리 함수
def preprocess_image(image):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    img_tensor = transform(image)
    return img_tensor.numpy()

# 예측 함수
def predict(image):
    input_data = preprocess_image(image)
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: input_data.reshape(1, 3, 224, 224)})
    probabilities = torch.nn.functional.softmax(torch.tensor(outputs[0][0]), dim=0)
    predicted_class_idx = probabilities.argmax().item()
    predicted_class_label = CLASS_LABELS.get(predicted_class_idx, f"알 수 없는 클래스 {predicted_class_idx}")
    confidence = probabilities[predicted_class_idx].item()
    
    return {
        "class": predicted_class_label,
        "confidence": float(confidence),
        "class_index": predicted_class_idx
    }

# kiwi_model 엔드포인트 추가
@app.post("/kiwi_predict")
async def kiwi_predict(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}")
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        result = predict(image)
        logger.info(f"Prediction result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# 챗봇 엔드포인트
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    농산물 재배법에 답해 드립니다. - 농산물 재배법 상담 챗봇
    """
    try:
        # 기존 대화 기록 가져오기
        conversation_history = app.state.conversation_history

        # 현재 사용자의 입력 메시지 가져오기
        current_message = request.contents[-1].parts[0].get("text", "") if request.contents else ""

        # AI 응답 생성
        response = await process_query(current_message, conversation_history)

        # 응답 변환 및 반환
        return ChatResponse(
            candidates=[
                ChatCandidate(
                    content=ChatMessage(
                        role="model",
                        parts=[
                            {
                                "text": response
                            }
                        ]
                    )
                )
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'오류 발생: {str(e)}')

@app.post("/reset")
async def reset_conversation():
    """
    대화 기록 초기화
    """
    app.state.conversation_history.clear()
    return {"message": "대화 기록이 초기화 되었습니다."}

# 데이터베이스 설정
load_dotenv()

# PostgreSQL 연결 문자열 구성
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

if not all([DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT]):
    raise ValueError("필수 환경 변수가 설정되지 않았습니다.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 댓글 모델 정의
class Comment(BaseModel):
    comment_id: int
    post_id: int
    user_id: str
    content: str
    created_at: datetime

class CommentCreate(BaseModel):
    post_id: int
    content: str
    user_email: str

class CommentUpdate(BaseModel):
    content: str

# JWT 설정
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
def read_root():
    return {"message": "농산물 가격 정보 API"}

@app.get("/api/price")
async def get_price():
    try:
        result = get_price_data()
        if result is None:
            raise HTTPException(status_code=500, detail="데이터를 가져오는데 실패했습니다")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 댓글 조회
@app.get("/api/comments/{post_id}")
async def get_comments(post_id: int):
    try:
        db = SessionLocal()
        result = db.execute(
            text("""
                SELECT c.*, a.email 
                FROM comments c 
                JOIN auth a ON c.user_id = a.user_id 
                WHERE c.post_id = :post_id 
                ORDER BY c.created_at DESC
            """),
            {"post_id": post_id}
        )
        comments = result.fetchall()
        
        comments_data = []
        for comment in comments:
            comment_dict = {
                "comment_id": comment.comment_id,
                "post_id": comment.post_id,
                "user_id": comment.user_id,
                "content": comment.content,
                "created_at": comment.created_at,
                "email": comment.email
            }
            comments_data.append(comment_dict)
        
        return {
            "success": True,
            "data": comments_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# 댓글 작성
@app.post("/api/comments")
async def create_comment(comment: CommentCreate):
    try:
        db = SessionLocal()
        
        # 사용자 ID 조회
        user_query = text("SELECT user_id FROM auth WHERE email = :email")
        user_result = db.execute(user_query, {"email": comment.user_email})
        user_id = user_result.scalar()
        
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 댓글 작성
        query = text("""
            INSERT INTO comments (post_id, user_id, content, created_at)
            VALUES (:post_id, :user_id, :content, NOW())
            RETURNING comment_id, post_id, user_id, content, created_at
        """)
        
        result = db.execute(
            query,
            {
                "post_id": comment.post_id,
                "user_id": user_id,
                "content": comment.content
            }
        )
        db.commit()
        
        new_comment = result.fetchone()
        
        return {
            "success": True,
            "data": {
                "comment_id": new_comment.comment_id,
                "post_id": new_comment.post_id,
                "user_id": new_comment.user_id,
                "content": new_comment.content,
                "created_at": new_comment.created_at,
                "email": comment.user_email
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# 댓글 수정
@app.put("/api/comments/{comment_id}")
async def update_comment(
    comment_id: int, 
    comment_data: dict,
    authorization: str = Header(None)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="유효하지 않은 인증 토큰입니다")
            
        token = authorization.split(" ")[1]
        try:
            current_user = await get_current_user(token)
            logging.info(f"인증된 사용자: {current_user}")
        except Exception as e:
            logging.error(f"토큰 검증 실패: {str(e)}")
            raise HTTPException(status_code=401, detail="인증이 만료되었거나 유효하지 않은 토큰입니다")
        
        db = SessionLocal()
        
        # 프론트엔드 데이터에서 필요한 정보 추출
        content = comment_data.get("content")
        user_email = comment_data.get("userEmail")
        
        logging.info(f"받은 데이터: content={content}, user_email={user_email}")
        
        if not content or not user_email:
            raise HTTPException(status_code=400, detail="필수 데이터가 누락되었습니다")
        
        # 댓글 작성자 확인
        check_query = text("""
            SELECT c.user_id, a.email 
            FROM comments c 
            JOIN auth a ON c.user_id = a.user_id 
            WHERE c.comment_id = :comment_id
        """)
        result = db.execute(check_query, {"comment_id": comment_id})
        comment = result.fetchone()
        
        if not comment:
            raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다")
        if comment.email != user_email:
            raise HTTPException(status_code=403, detail="댓글을 수정할 권한이 없습니다")
        
        # 댓글 수정
        update_query = text("""
            UPDATE comments 
            SET content = :content 
            WHERE comment_id = :comment_id
            RETURNING comment_id, post_id, user_id, content, created_at
        """)
        
        result = db.execute(update_query, {
            "content": content,
            "comment_id": comment_id
        })
        db.commit()
        
        updated_comment = result.fetchone()
        
        return {
            "success": True,
            "data": {
                "comment_id": updated_comment.comment_id,
                "post_id": updated_comment.post_id,
                "user_id": updated_comment.user_id,
                "content": updated_comment.content,
                "created_at": updated_comment.created_at,
                "email": user_email
            }
        }
        
    except Exception as e:
        db.rollback()
        logging.error(f"댓글 수정 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# 댓글 삭제
@app.delete("/api/comments/{comment_id}")
async def delete_comment(comment_id: int, user_email: str):
    try:
        db = SessionLocal()
        
        # 댓글 작성자 확인
        check_query = text("""
            SELECT c.user_id, a.email 
            FROM comments c 
            JOIN auth a ON c.user_id = a.user_id 
            WHERE c.comment_id = :comment_id
        """)
        result = db.execute(check_query, {"comment_id": comment_id})
        comment = result.fetchone()
        
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        if comment.email != user_email:
            raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
        
        # 댓글 삭제
        db.execute(
            text("DELETE FROM comments WHERE comment_id = :comment_id"),
            {"comment_id": comment_id}
        )
        db.commit()
        
        return {"success": True, "message": "Comment deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
