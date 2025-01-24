-- Auth 테이블 생성
CREATE TABLE "Auth" (
    "user_id" SERIAL NOT NULL,          -- 자동 증가 ID
    "email" VARCHAR(100) NOT NULL,      -- 이메일
    "password" VARCHAR(255) NOT NULL,   -- 비밀번호
    "birth_date" DATE NULL,             -- 생년월일 
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 생성일자
    CONSTRAINT "PK_AUTH" PRIMARY KEY ("user_id") -- 기본 키
);

-- Post 테이블 생성
CREATE TABLE "Post" (
    "post_id" SERIAL NOT NULL,          -- 게시글 ID
    "user_id" INT NOT NULL,             -- 작성자 ID (외래 키)
    "title" VARCHAR(50) NOT NULL,       -- 게시글 제목
    "name" VARCHAR(10) NULL,            -- 작성자 이름
    "content" VARCHAR(100) NULL,        -- 게시글 내용 
    "date" DATE DEFAULT CURRENT_DATE,   -- 게시글 작성 날짜
    CONSTRAINT "PK_POST" PRIMARY KEY ("post_id"), -- 기본 키
    CONSTRAINT "FK_Auth_TO_Post_1" FOREIGN KEY ("user_id") REFERENCES "Auth" ("user_id") -- 외래 키
    ON DELETE CASCADE                   -- 작성자 삭제 시 게시글 삭제
);