-- Auth 테이블 생성
CREATE TABLE Auth (
    "user_id" SERIAL NOT NULL,          -- 자동 증가 ID
    "email" VARCHAR(100) NOT NULL,      -- 이메일
    "password" VARCHAR(255) NOT NULL,   -- 비밀번호
    "birth_date" DATE NULL,             -- 생년월일 
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 생성일자
    CONSTRAINT "PK_AUTH" PRIMARY KEY ("user_id") -- 기본 키
);

-- Write 테이블 생성
CREATE TABLE Write (
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

-- top_10_sales 테이블 생성
CREATE TABLE "top_10_sales" (
	"Key" VARCHAR(255) NOT NULL, -- 기본 키
	"category" VARCHAR(50) NULL, -- 카테고리
	"previous_year"	NUMERIC NULL, -- 전년도
	"base_date"	NUMERIC NULL -- 기준 날짜
);

-- sales_data_2024 테이블 생성
CREATE TABLE "sales_data_2024" (
	"week" VARCHAR(10) NOT NULL, -- 주차
	"persimmon" NUMERIC NULL, -- 감
	"mandarin" NUMERIC NULL, -- 만다린오렌지
	"dried_pepper" NUMERIC NULL, -- 건고추
	"dried_anchovy" NUMERIC NULL, -- 건멸치
	"sweet_potato" NUMERIC NULL, -- 고구마
	"oyster" NUMERIC NULL, -- 굴
	"seaweed" NUMERIC NULL, -- 미역
	"green_onion" NUMERIC NULL, -- 대파
	"strawberry" NUMERIC NULL, -- 딸기
	"garlic" NUMERIC NULL, -- 마늘
	"radish" NUMERIC NULL, -- 무
	"squid" NUMERIC NULL, -- 오징어
	"banana" NUMERIC NULL, -- 바나나
	"cherry_tomato" NUMERIC NULL, -- 방울토마토
	"pear" NUMERIC NULL -- 배
);

-- Auth 테이블 제약 조건 추가
ALTER TABLE "Auth" ADD CONSTRAINT "PK_AUTH" PRIMARY KEY (
	"user_id" -- 기본 키
);

-- top_10_sales 테이블 제약 조건 추가
ALTER TABLE "top_10_sales" ADD CONSTRAINT "PK_TOP_10_SALES" PRIMARY KEY (
	"Key" -- 기본 키
);

-- Write 테이블 제약 조건 추가
ALTER TABLE "Write" ADD CONSTRAINT "PK_POST" PRIMARY KEY (
	"post_id", -- 기본 키
	"user_id" -- 기본 키
);

-- sales_data_2024 테이블 제약 조건 추가
ALTER TABLE "sales_data_2024" ADD CONSTRAINT "PK_SALES_DATA_2024" PRIMARY KEY (
	"week" -- 기본 키
);

-- Write 테이블 외래 키 추가 
ALTER TABLE "Write" ADD CONSTRAINT "FK_Auth_TO_Post_1" FOREIGN KEY (
	"user_id" -- 외래 키
)
REFERENCES "Auth" (
	"user_id" -- 기본 키
)
ON DELETE CASCADE;