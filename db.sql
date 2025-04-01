CREATE TABLE "growth_calendar" (
	"calendar_id"	SERIAL PRIMARY KEY,
	"user_id"	integer		NOT NULL,
	"region"	character varying(100)		NULL,
	"crop"	character varying(100)		NULL,
	"growth_date"	date		NULL,
	"created_at"	timestamp without time zone		NULL
);

CREATE TABLE "crops" (
	"crop_id"	SERIAL PRIMARY KEY,
	"crop_name"	character varying(50)		NULL,
	"revenue_per_hour"	numeric(10,2)		NULL,
	"revenue_per_3_3m"	numeric(10,2)		NULL,
	"annual_sales"	numeric(10,2)		NULL,
	"total_cost"	numeric(10,2)		NULL
);

CREATE TABLE "crop_costs" (
	"cost_id"	SERIAL PRIMARY KEY,
	"crop_id"	integer		NOT NULL,
	"cost_type"	character varying(50)		NULL,
	"amount"	numeric(10,2)		NULL
);

CREATE TABLE "market_data" (
	"key"	SERIAL PRIMARY KEY,
	"year"	bigint		NULL,
	"week"	bigint		NULL,
	"갈치"	double precision		NULL,
	"감"	double precision		NULL,
	"감귤"	double precision		NULL,
	"건고추"	double precision		NULL,
	"건멸치"	double precision		NULL,
	"고구마"	double precision		NULL,
	"굴"	double precision		NULL,
	"김"	double precision		NULL,
	"대파"	double precision		NULL,
	"딸기"	double precision		NULL,
	"마늘"	double precision		NULL,
	"무"	double precision		NULL,
	"물오징어"	double precision		NULL,
	"바나나"	double precision		NULL,
	"방울토마토"	double precision		NULL,
	"배"	double precision		NULL,
	"배추"	double precision		NULL,
	"복숭아"	double precision		NULL,
	"사과"	double precision		NULL,
	"상추"	double precision		NULL,
	"새우"	double precision		NULL,
	"수박"	double precision		NULL,
	"시금치"	double precision		NULL,
	"쌀"	double precision		NULL,
	"양파"	double precision		NULL,
	"오렌지"	double precision		NULL,
	"오이"	double precision		NULL,
	"전복"	double precision		NULL,
	"참다래"	double precision		NULL,
	"참외"	double precision		NULL,
	"찹쌀"	double precision		NULL,
	"체리"	double precision		NULL,
	"토마토"	double precision		NULL,
	"포도"	double precision		NULL
);

CREATE TABLE "quiz" (
	"key"	SERIAL PRIMARY KEY,
	"crop"	character varying(50)		NULL,
	"question"	text		NULL,
	"option_1"	text		NULL,
	"option_2"	text		NULL,
	"option_3"	text		NULL,
	"option_4"	text		NULL,
	"correct_answer"	text		NULL
);

CREATE TABLE "auth" (
	"user_id"	SERIAL PRIMARY KEY,
	"email"	character varying(100)		NULL,
	"password"	character varying(255)		NULL,
	"birth_date"	date		NULL,
	"created_at"	timestamp without time zone		NULL
);

CREATE TABLE "sales_data" (
	"crop_name" text NULL,
	"previous_year" bigint NULL,
	"current_year" bigint NULL
);

CREATE TABLE "write" (
	"post_id"	SERIAL PRIMARY KEY,
	"user_id"	integer		NOT NULL,
	"title"	character varying(50)		NULL,
	"content"	text		NULL,
	"date"	date		NULL,
	"category"	character varying(10)		NULL,
	"community_type"	character varying(50)		NULL
);

CREATE TABLE "comments" (
	"comment_id"	SERIAL PRIMARY KEY,
	"post_id"	integer		NOT NULL,
	"user_id"	integer		NOT NULL,
	"content"	text		NULL,
	"created_at"	timestamp without time zone		NULL,
	"community_type"	character varying(50)		NULL,
	"parent_id"	integer		NULL
);

CREATE TABLE "price_data" (
	"id"	SERIAL PRIMARY KEY,
	"item_name"	character varying(50)		NULL,
	"price"	character varying(50)		NULL,
	"unit"	character varying(20)		NULL,
	"date"	date		NULL,
	"previous_date"	date		NULL,
	"price_change"	integer		NULL,
	"yesterday_price"	integer		NULL,
	"category_code"	character varying(10)		NULL,
	"category_name"	character varying(50)		NULL,
	"has_dpr1"	boolean		NULL,
	"created_at"	timestamp without time zone		NULL
);

-- crops 테이블에 기본 데이터 입력
INSERT INTO crops(id, crop_name, revenue_per_3_3m, revenue_per_hour, annual_sales, total_cost) 
VALUES 
(1, '감자', 16153, 60028, 1615298, 834725),
(2, '고구마', 12666, 44500, 1266574, 603672),
(3, '당근', 13304, 44175, 1330337, 707890),
(4, '사과', 21456, 42452, 2134383, 1046274),
(5, '배추', 9069, 54974, 906830, 488298);

-- crop_costs 테이블에 경영비 상세 데이터 입력
INSERT INTO crop_costs (id, crop_id, cost_type, amount) 
VALUES 
-- 감자 경영비 상세
(1, 1, '수도광열비', 45073),
(2, 1, '기타재료비', 177834),
(3, 1, '소농구비', 1503),
(4, 1, '대농구상각비', 45488),
(5, 1, '영농시설상각비', 104286),
(6, 1, '수리유지비', 799),
(7, 1, '기타비용', 981),
(8, 1, '농기계시설임차료', 9273),
(9, 1, '토지임차료', 32791),
(10, 1, '위탁영농비', 18040),
(11, 1, '고용노동비', 117085),
(12, 1, '종자종묘비', 160415),
(13, 1, '보통비료비', 50323),
(14, 1, '부산물비료비', 57223),
(15, 1, '농약비', 13611),

-- 고구마 경영비 상세
(16, 2, '수도광열비', 16031),
(17, 2, '기타재료비', 66121),
(18, 2, '소농구비', 1503),
(19, 2, '대농구상각비', 57864),
(20, 2, '영농시설상각비', 33976),
(21, 2, '수리유지비', 3694),
(22, 2, '기타비용', 3337),
(23, 2, '농기계시설임차료', 5280),
(24, 2, '토지임차료', 58030),
(25, 2, '위탁영농비', 7553),
(26, 2, '고용노동비', 177098),
(27, 2, '종자종묘비', 122067),
(28, 2, '보통비료비', 21207),
(29, 2, '부산물비료비', 19774),
(30, 2, '농약비', 10137),

-- 당근 경영비 상세
(31, 3, '수도광열비', 19028),
(32, 3, '기타재료비', 69076),
(33, 3, '소농구비', 208),
(34, 3, '대농구상각비', 61033),
(35, 3, '영농시설상각비', 40413),
(36, 3, '수리유지비', 10710),
(37, 3, '기타비용', 1095),
(38, 3, '농기계시설임차료', 3635),
(39, 3, '토지임차료', 63708),
(40, 3, '위탁영농비', 30505),
(41, 3, '고용노동비', 214234),
(42, 3, '종자종묘비', 75144),
(43, 3, '보통비료비', 37743),
(44, 3, '부산물비료비', 49995),
(45, 3, '농약비', 31363),

-- 사과 경영비 상세
(46, 4, '수도광열비', 49443),
(47, 4, '기타재료비', 125043),
(48, 4, '소농구비', 3567),
(49, 4, '대농구상각비', 163770),
(50, 4, '영농시설상각비', 78948),
(51, 4, '수리유지비', 17172),
(52, 4, '기타비용', 31175),
(53, 4, '농기계시설임차료', 3602),
(54, 4, '토지임차료', 17641),
(55, 4, '위탁영농비', 1039),
(56, 4, '고용노동비', 212377),
(57, 4, '종자종묘비', 122773),
(58, 4, '보통비료비', 23190),
(59, 4, '부산물비료비', 37672),
(60, 4, '농약비', 158862),

-- 배추 경영비 상세
(61, 5, '수도광열비', 12955),
(62, 5, '기타재료비', 15146),
(63, 5, '소농구비', 1107),
(64, 5, '대농구상각비', 45906),
(65, 5, '영농시설상각비', 8965),
(66, 5, '수리유지비', 5687),
(67, 5, '기타비용', 931),
(68, 5, '농기계시설임차료', 1146),
(69, 5, '토지임차료', 48535),
(70, 5, '위탁영농비', 20615),
(71, 5, '고용노동비', 110579),
(72, 5, '종자종묘비', 39461),
(73, 5, '보통비료비', 54708),
(74, 5, '부산물비료비', 52752),
(75, 5, '농약비', 69805);