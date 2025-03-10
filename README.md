# 농산물 가격 정보 API 백엔드

농산물 가격 정보 및 예측, 커뮤니티 기능을 제공하는 백엔드 API 서버입니다.

## 기술 스택

- Python
- FastAPI
- PostgreSQL
- JWT 인증
- ONNX Runtime (이미지 분석)

## 시작하기

### 사전 요구사항

- Python 3.8 이상
- PostgreSQL
- Node.js (일부 기능에 필요)

### 환경 설정

1. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 의존성 설치

```bash
pip install -r requirements.txt
npm install  # 일부 기능에 필요한 Node.js 패키지 설치
```

3. 환경 변수 설정
   `.env` 파일을 생성하고 다음 내용을 설정하세요:

```
DB_HOST=localhost
DB_USER=your_db_user
DB_PASS=your_db_password
DB_NAME=your_db_name
DB_PORT=5432
JWT_SECRET=your_jwt_secret
```

4. 데이터베이스 설정

```bash
psql -U your_db_user -d your_db_name -f db.sql
```

## 모델 파일 설정

### 모델 파일 다운로드

프로젝트에 필요한 모델 파일들은 다음 위치에서 다운로드 받을 수 있습니다:

- plant_classifier.onnx
- disease_classifier.onnx

다운로드 받은 파일들은 `images_model/chamoe_model/models/` 디렉토리에 위치시켜주세요.

※ 모델 파일들은 용량 문제로 인해 Git에서 제외되어 있습니다.

모델 파일 다운로드 링크: [https://drive.google.com/drive/folders/19iXxf-TJ3dozoNjvH8kd5uuv6KnoWvFl]

## 서버 실행

```bash
uvicorn app:app --reload
```

서버는 기본적으로 http://localhost:8000 에서 실행됩니다.

## API 문서

API 문서는 Swagger UI를 통해 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 주요 기능

### 1. 농산물 정보

- 도시별 날씨 정보 조회
- 참외 질병 예측
- 작물 가격 예측
- 위성 이미지 정보
- 농산물 가격 정보
- 시장 정보

### 2. 사용자 관리

- 회원가입
- 로그인 (JWT 인증)

### 3. 커뮤니티

- 게시글 작성
- 댓글 조회/작성
- 카테고리별 게시판 (텃밭, 마켓, 자유게시판)

## 프로젝트 구조

```
back/
├── app.py              # 메인 애플리케이션
├── backend.py          # 백엔드 로직
├── chatbot.py          # 챗봇 기능
├── routes/             # API 라우트
├── utils/             # 유틸리티 함수
├── images_model/      # 이미지 분석 모델
├── testdata/         # 테스트 데이터
├── testpython/       # 가격 예측 모델
└── db.sql            # 데이터베이스 스키마
```

## 테스트

테스트를 실행하려면:

```bash
python -m pytest test.py test_comments.py
```

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
