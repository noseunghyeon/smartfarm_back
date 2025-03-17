from fastapi import FastAPI, HTTPException, Depends, Header, File, UploadFile, Security
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
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
import jwt
from chatbot import process_query, ChatMessage, ChatRequest, ChatCandidate, ChatResponse
from image_classifier import classifier, ImageClassificationResponse
from PIL import Image
import io

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

# JWT 관련 설정
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

# OAuth2 스키마 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

security = HTTPBearer()

# 현재 사용자 가져오기 함수
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        logger.info("토큰 검증 시작")
        
        if not token:
            logger.error("토큰이 없음")
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        try:
            # JWT 토큰 디코딩
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            
            if email is None:
                logger.error("토큰에 이메일 정보가 없음")
                raise HTTPException(
                    status_code=401, 
                    detail="Could not validate credentials"
                )
                
            logger.info(f"토큰에서 추출한 이메일: {email}")
            return email
            
        except jwt.PyJWTError as e:
            logger.error(f"JWT 검증 실패: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except Exception as e:
        logger.error(f"토큰 검증 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

# 먼저 특정 경로를 정의
@app.get("/api/comments/user")
async def get_my_comments(authorization: str = Header(None)):
    try:
        logger.info("댓글 조회 시작")
        
        # 토큰 검증
        if not authorization or not authorization.startswith("Bearer "):
            logger.error("인증 헤더가 없거나 잘못된 형식")
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header"
            )
        
        token = authorization.split(" ")[1]
        try:
            # JWT 토큰 디코딩
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            current_user = payload.get("sub")  # 이메일 추출
            
            if not current_user:
                logger.error("토큰에 이메일 정보가 없음")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token payload"
                )
                
            logger.info(f"인증된 사용자: {current_user}")
            
        except jwt.ExpiredSignatureError:
            logger.error("만료된 토큰")
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.JWTError as e:
            logger.error(f"JWT 검증 실패: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials"
            )
        
        db = SessionLocal()
        
        # 사용자 ID 조회
        user_query = text("SELECT user_id FROM auth WHERE email = :email")
        user_result = db.execute(user_query, {"email": current_user})
        user_id = user_result.scalar()
        
        if not user_id:
            logger.error(f"사용자를 찾을 수 없음: {current_user}")
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        logger.info(f"사용자 ID: {user_id}")
        
        # 댓글 조회
        comments_query = text("""
            SELECT c.*, w.title as post_title, a.email 
            FROM comments c 
            JOIN write w ON c.post_id = w.post_id 
            JOIN auth a ON c.user_id = a.user_id 
            WHERE c.user_id = :user_id 
            ORDER BY c.created_at DESC
        """)
        
        result = db.execute(comments_query, {"user_id": user_id})
        comments = result.fetchall()
        
        logger.info(f"조회된 댓글 수: {len(comments) if comments else 0}")
        
        comments_data = []
        for comment in comments:
            comment_dict = {
                "comment_id": comment.comment_id,
                "post_id": comment.post_id,
                "post_title": comment.post_title,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "email": comment.email
            }
            comments_data.append(comment_dict)
        
        return {
            "success": True,
            "data": comments_data,
            "message": "댓글 조회 성공"
        }
        
    except Exception as e:
        logger.error(f"댓글 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'db' in locals():
            db.close()

# 그 다음 동적 파라미터를 사용하는 경로를 정의
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

# 내 게시글 조회 엔드포인트 수정
@app.get("/api/write/user")
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

# 이미지 분류 엔드포인트들
@app.post("/kiwi_predict", response_model=ImageClassificationResponse)
async def kiwi_predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        result = await classifier.classify_kiwi(image)
        return result
    except Exception as e:
        logger.error(f"키위 예측 처리 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/chamoe_predict", response_model=ImageClassificationResponse)
async def chamoe_predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        result = await classifier.classify_chamoe(image)
        return result
    except Exception as e:
        logger.error(f"참외 예측 처리 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/plant_predict", response_model=ImageClassificationResponse)
async def plant_predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        result = await classifier.classify_plant(image)
        return result
    except Exception as e:
        logger.error(f"식물 분류 처리 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
