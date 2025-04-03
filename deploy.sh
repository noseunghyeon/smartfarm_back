#!/bin/bash

# 기존 컨테이너 중지 및 삭제
docker-compose -f docker-compose.prod.yml down

# 최신 이미지 가져오기
docker pull roseunghyeon/smartfarm-back:latest

# 컨테이너 시작
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f 