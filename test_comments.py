import asyncio
import httpx
import json

async def test_create_comment():
    print("\n=== 댓글 작성 테스트 ===")
    async with httpx.AsyncClient() as client:
        # 테스트용 댓글 데이터
        comment_data = {
            "post_id": 86,  # 실제 존재하는 게시글 ID로 변경하세요
            "content": "테스트 댓글입니다."
        }
        
        # JWT 토큰 (실제 로그인해서 받은 토큰으로 변경하세요)
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMTA2aXVAbmF2ZXIuY29tIiwiZXhwIjoxNzQxMTQ0ODgwfQ.xIsRUiTF3VDhhC865KC1lAXTDXu7Ql-JoFqiENAKXZM"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            # 댓글 작성 테스트
            response = await client.post(
                "http://localhost:8000/api/comments",
                json=comment_data,
                headers=headers
            )
            
            print("응답 상태 코드:", response.status_code)
            print("응답 내용:", response.json())
            
            if response.status_code == 201 or response.status_code == 200:
                print("✅ 댓글 작성 성공!")
            else:
                print("❌ 댓글 작성 실패")
                
        except Exception as e:
            print("❌ 오류 발생:", str(e))

async def test_get_comments():
    print("\n=== 댓글 조회 테스트 ===")
    async with httpx.AsyncClient() as client:
        post_id = 86  # 실제 존재하는 게시글 ID로 변경하세요
        
        try:
            # 댓글 조회 테스트
            response = await client.get(f"http://localhost:8000/api/comments/{post_id}")
            
            print("응답 상태 코드:", response.status_code)
            print("응답 내용:", response.json())
            
            if response.status_code == 200:
                print("✅ 댓글 조회 성공!")
            else:
                print("❌ 댓글 조회 실패")
                
        except Exception as e:
            print("❌ 오류 발생:", str(e))

async def run_tests():
    # 댓글 작성 테스트
    await test_create_comment()
    
    # 댓글 조회 테스트
    await test_get_comments()

if __name__ == "__main__":
    print("댓글 기능 테스트를 시작합니다...")
    asyncio.run(run_tests()) 