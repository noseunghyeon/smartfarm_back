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

CREATE TABLE "top_10_sales" (
	"Key"	VARCHAR(255)		NOT NULL,
	"category"	VARCHAR(50)		NULL,
	"previous_year"	NUMERIC		NULL,
	"base_date"	NUMERIC		NULL
);

CREATE TABLE "sales_data_2024" (
	"week"	VARCHAR(10)		NOT NULL,
	"persimmon"	NUMERIC		NULL,
	"mandarin"	NUMERIC		NULL,
	"dried_pepper"	NUMERIC		NULL,
	"dried_anchovy"	NUMERIC		NULL,
	"sweet_potato"	NUMERIC		NULL,
	"oyster"	NUMERIC		NULL,
	"seaweed"	NUMERIC		NULL,
	"green_onion"	NUMERIC		NULL,
	"strawberry"	NUMERIC		NULL,
	"garlic"	NUMERIC		NULL,
	"radish"	NUMERIC		NULL,
	"squid"	NUMERIC		NULL,
	"banana"	NUMERIC		NULL,
	"cherry_tomato"	NUMERIC		NULL,
	"pear"	NUMERIC		NULL
);

ALTER TABLE "Auth" ADD CONSTRAINT "PK_AUTH" PRIMARY KEY (
	"user_id"
);

ALTER TABLE "top_10_sales" ADD CONSTRAINT "PK_TOP_10_SALES" PRIMARY KEY (
	"Key"
);

ALTER TABLE "Write" ADD CONSTRAINT "PK_POST" PRIMARY KEY (
	"post_id",
	"user_id"
);

ALTER TABLE "sales_data_2024" ADD CONSTRAINT "PK_SALES_DATA_2024" PRIMARY KEY (
	"week"
);

ALTER TABLE "Write" ADD CONSTRAINT "FK_Auth_TO_Post_1" FOREIGN KEY (
	"user_id"
)
REFERENCES "Auth" (
	"user_id"
);