-- 사용자 테이블 생성
CREATE TABLE auth (
	key integer NOT NULL,
	email varchar(100) NULL,
	password varchar(255) NULL,
	birth_date date NULL,
	created_at timestamp NULL
);

-- 판매 데이터 테이블 생성
CREATE TABLE sales_data (
	category varchar(50) NULL,
	previous_year numeric NULL,
	base_date numeric NULL
);

-- 게시글 테이블 생성
CREATE TABLE write (
	post_id integer NOT NULL,
	user_id integer NOT NULL,
	title varchar(50) NULL,
	content varchar(700) NULL,
	date date NULL,
	category varchar(10) NULL,
	community_type varchar NULL
);

-- 댓글 테이블 생성
CREATE TABLE comments (
	key integer NOT NULL,
	post_id integer NOT NULL,
	user_id integer NOT NULL,
	content text NULL,
	created_at timestamp NULL,
	community_type varchar NULL,
	parent_id integer NULL
);

-- 시장 데이터 테이블 생성
CREATE TABLE market_data (
	year bigint NULL,
	week bigint NULL,
	갈치 double precision NULL,
	감 double precision NULL,
	감귤 double precision NULL,
	건고추 double precision NULL,
	건멸치 double precision NULL,
	고구마 double precision NULL,
	굴 double precision NULL,
	김 double precision NULL,
	대파 double precision NULL,
	딸기 double precision NULL,
	마늘 double precision NULL,
	무 double precision NULL,
	물오징어 double precision NULL,
	바나나 double precision NULL,
	방울토마토 double precision NULL,
	배 double precision NULL,
	배추 double precision NULL,
	복숭아 double precision NULL,
	사과 double precision NULL,
	상추 double precision NULL,
	새우 double precision NULL,
	수박 double precision NULL,
	시금치 double precision NULL,
	쌀 double precision NULL,
	양파 double precision NULL,
	오렌지 double precision NULL,
	오이 double precision NULL,
	전복 double precision NULL,
	참다래 double precision NULL,
	참외 double precision NULL,
	찹쌀 double precision NULL,
	체리 double precision NULL,
	토마토 double precision NULL,
	포도 double precision NULL
);

-- 작물 캘린더 테이블 생성
CREATE TABLE growth_calendar (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    region VARCHAR(100) NOT NULL,
    crop VARCHAR(100) NOT NULL,
    growth_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth(user_id) ON DELETE CASCADE
);

-- 가격 데이터 테이블 생성
CREATE TABLE price_data (
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    price VARCHAR(50) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    previous_date DATE NOT NULL,
    price_change INTEGER NOT NULL,
    yesterday_price INTEGER NOT NULL,
    category_code VARCHAR(10) NOT NULL,
    category_name VARCHAR(50) NOT NULL,
    has_dpr1 BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE auth ADD CONSTRAINT pk_auth PRIMARY KEY (key);

ALTER TABLE write ADD CONSTRAINT pk_write PRIMARY KEY (post_id, user_id);

ALTER TABLE comments ADD CONSTRAINT pk_comments PRIMARY KEY (key, post_id, user_id);

ALTER TABLE write ADD CONSTRAINT fk_auth_to_write_1 FOREIGN KEY (user_id) REFERENCES auth (key);

ALTER TABLE comments ADD CONSTRAINT fk_auth_to_comments_1 FOREIGN KEY (post_id) REFERENCES auth (key);

ALTER TABLE comments ADD CONSTRAINT fk_write_to_comments_1 FOREIGN KEY (user_id) REFERENCES write (user_id);

ALTER TABLE growth_calendar ADD CONSTRAINT fk_auth_to_growth_calendar_1 FOREIGN KEY (user_id) REFERENCES auth (key);