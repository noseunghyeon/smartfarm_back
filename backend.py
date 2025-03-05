from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from test import get_price_data

app = FastAPI()

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    comment_update: CommentUpdate,
    user_email: str
):
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
            raise HTTPException(status_code=403, detail="Not authorized to update this comment")
        
        # 댓글 수정
        update_query = text("""
            UPDATE comments 
            SET content = :content 
            WHERE comment_id = :comment_id
            RETURNING *
        """)
        
        result = db.execute(update_query, {
            "content": comment_update.content,
            "comment_id": comment_id
        })
        db.commit()
        
        updated_comment = result.fetchone()
        return {"success": True, "data": dict(updated_comment)}
        
    except Exception as e:
        db.rollback()
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
