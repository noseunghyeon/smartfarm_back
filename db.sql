CREATE TABLE `auth` (
	`key`	[PK] integer	NOT NULL,
	`email`	character varying(100)	NULL,
	`password`	character varying(255)	NULL,
	`birth_date`	date	NULL,
	`created_at`	timestamp without time zone	NULL
);

CREATE TABLE `sales_data` (
	`category`	character varying(50)	NULL,
	`previous_year`	numeric	NULL,
	`base_date`	numeric	NULL
);

CREATE TABLE `write` (
	`post_id`	[PK] integer	NOT NULL,
	`user_id`	[FK} integer	NOT NULL,
	`title`	character varying(50)	NULL,
	`content`	character varying(700)	NULL,
	`date`	date	NULL,
	`category`	character varying(10)	NULL,
	`community_type`	community_type	NULL
);

CREATE TABLE `comments` (
	`Key`	[PK] integer	NOT NULL,
	`post_id`	[FK} integer	NOT NULL,
	`user_id`	[FK} integer	NOT NULL,
	`content`	text	NULL,
	`created_at`	timestamp without time zone	NULL,
	`community_type`	character varying	NULL,
	`parent_id`	integer	NULL
);

CREATE TABLE `market_data` (
	`year`	bigint	NULL,
	`week`	bigint	NULL,
	`갈치`	double precision	NULL,
	`감`	double precision	NULL,
	`감귤`	double precision	NULL,
	`건고추`	double precision	NULL,
	`건멸치`	double precision	NULL,
	`고구마`	double precision	NULL,
	`굴`	double precision	NULL,
	`김`	double precision	NULL,
	`대파`	double precision	NULL,
	`딸기`	double precision	NULL,
	`마늘`	double precision	NULL,
	`무`	double precision	NULL,
	`물오징어`	double precision	NULL,
	`바나나`	double precision	NULL,
	`방울토마토`	double precision	NULL,
	`배`	double precision	NULL,
	`배추`	double precision	NULL,
	`복숭아`	double precision	NULL,
	`사과`	double precision	NULL,
	`상추`	double precision	NULL,
	`새우`	double precision	NULL,
	`수박`	double precision	NULL,
	`시금치`	double precision	NULL,
	`쌀`	double precision	NULL,
	`양파`	double precision	NULL,
	`오렌지`	double precision	NULL,
	`오이`	double precision	NULL,
	`전복`	double precision	NULL,
	`참다래`	double precision	NULL,
	`참외`	double precision	NULL,
	`찹쌀`	double precision	NULL,
	`체리`	double precision	NULL,
	`토마토`	double precision	NULL,
	`포도`	double precision	NULL
);

ALTER TABLE `auth` ADD CONSTRAINT `PK_AUTH` PRIMARY KEY (
	`key`
);

ALTER TABLE `write` ADD CONSTRAINT `PK_WRITE` PRIMARY KEY (
	`post_id`,
	`user_id`
);

ALTER TABLE `comments` ADD CONSTRAINT `PK_COMMENTS` PRIMARY KEY (
	`Key`,
	`post_id`,
	`user_id`
);

ALTER TABLE `write` ADD CONSTRAINT `FK_auth_TO_write_1` FOREIGN KEY (
	`user_id`
)
REFERENCES `auth` (
	`key`
);

ALTER TABLE `comments` ADD CONSTRAINT `FK_auth_TO_comments_1` FOREIGN KEY (
	`post_id`
)
REFERENCES `auth` (
	`key`
);

ALTER TABLE `comments` ADD CONSTRAINT `FK_write_TO_comments_1` FOREIGN KEY (
	`user_id`
)
REFERENCES `write` (
	`user_id`
);
