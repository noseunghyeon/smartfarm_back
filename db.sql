CREATE TABLE auth (
	key integer NOT NULL,
	email varchar(100) NULL,
	password varchar(255) NULL,
	birth_date date NULL,
	created_at timestamp NULL
);

CREATE TABLE sales_data (
	category varchar(50) NULL,
	previous_year numeric NULL,
	base_date numeric NULL
);

CREATE TABLE write (
	post_id integer NOT NULL,
	user_id integer NOT NULL,
	title varchar(50) NULL,
	content varchar(700) NULL,
	date date NULL,
	category varchar(10) NULL,
	community_type varchar NULL
);

CREATE TABLE comments (
	key integer NOT NULL,
	post_id integer NOT NULL,
	user_id integer NOT NULL,
	content text NULL,
	created_at timestamp NULL,
	community_type varchar NULL,
	parent_id integer NULL
);

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

ALTER TABLE auth ADD CONSTRAINT pk_auth PRIMARY KEY (key);

ALTER TABLE write ADD CONSTRAINT pk_write PRIMARY KEY (post_id, user_id);

ALTER TABLE comments ADD CONSTRAINT pk_comments PRIMARY KEY (key, post_id, user_id);

ALTER TABLE write ADD CONSTRAINT fk_auth_to_write_1 FOREIGN KEY (user_id) REFERENCES auth (key);

ALTER TABLE comments ADD CONSTRAINT fk_auth_to_comments_1 FOREIGN KEY (post_id) REFERENCES auth (key);

ALTER TABLE comments ADD CONSTRAINT fk_write_to_comments_1 FOREIGN KEY (user_id) REFERENCES write (user_id);
