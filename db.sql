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

-- 작물 테이블 생성
CREATE TABLE IF NOT EXISTS crops (
    id INT PRIMARY KEY,
    crop_name VARCHAR(50) NOT NULL,
    revenue_per_3_3m DECIMAL(10,2),
    revenue_per_hour DECIMAL(10,2),
    annual_sales DECIMAL(10,2),
    total_cost DECIMAL(10,2)
);

-- 작물 경영비 상세 테이블 생성
CREATE TABLE IF NOT EXISTS crop_costs (
    id SERIAL PRIMARY KEY,
    crop_id INT NOT NULL,
    cost_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (crop_id) REFERENCES crops(id)
);

-- crops 테이블에 기본 데이터 입력
INSERT INTO crops (id, crop_name, revenue_per_3_3m, revenue_per_hour, annual_sales, total_cost) 
VALUES 
(1, '감자', 16153, 60028, 1615298, 834715),
(2, '고구마', 12666, 44500, 1266574, 603671),
(3, '당근', 13304, 44175, 1330337, 707891);

-- crop_costs 테이블에 경영비 상세 데이터 입력
INSERT INTO crop_costs (crop_id, cost_type, amount) 
VALUES 
-- 감자 경영비 상세
(1, '종자종묘비', 9273),
(1, '비료비', 32791),
(1, '농약비', 18040),
(1, '수도광열비', 117085),
(1, '기타재료비', 160415),
(1, '영농시설비', 50323),
(1, '수리유지비', 17223),
(1, '제재료비', 13611),
(1, '소농구비', 1503),
(1, '대농구상각비', 45486),
(1, '영농시설상각비', 104286),
(1, '수리유지비', 799),
(1, '기타자재비', 981),
(1, '수선(기계-시설)장비료', 177834),
(1, '토지임차료', 58030),
(1, '고용노동비', 7553),
(1, '위탁영농비', 177098),
(1, '판매및운송비', 122067),
(1, '기타비용', 21207),
(1, '농작물재해보험료', 19774),
(1, '농기계보험료', 10137),

-- 고구마 경영비 상세
(2, '종자종묘비', 16031),
(2, '비료비', 66121),
(2, '농약비', 1503),
(2, '수도광열비', 57864),
(2, '농구비', 33976),
(2, '영농시설비', 3694),
(2, '수리유지비', 3337),
(2, '제재료비', 5280),
(2, '소농구비', 58030),
(2, '대농구상각비', 7553),
(2, '영농시설상각비', 177098),
(2, '수리유지비', 122067),
(2, '기타자재비', 21207),
(2, '수선(기계-시설)장비료', 19774),
(2, '토지임차료', 10137),

-- 당근 경영비 상세
(3, '종자종묘비', 19028),
(3, '비료비', 69076),
(3, '농약비', 208),
(3, '수도광열비', 61033),
(3, '농구비', 40413),
(3, '영농시설비', 10710),
(3, '수리유지비', 1095),
(3, '제재료비', 3635),
(3, '소농구비', 63708),
(3, '대농구상각비', 30505),
(3, '영농시설상각비', 214234),
(3, '수리유지비', 75144),
(3, '기타자재비', 37743),
(3, '수선(기계-시설)장비료', 49995),
(3, '토지임차료', 31365);