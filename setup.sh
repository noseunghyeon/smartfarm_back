#!/bin/bash

# 시스템 업데이트
sudo apt-get update
sudo apt-get upgrade -y

# Docker 설치
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Docker 권한 설정
sudo usermod -aG docker $USER

# Git 설치
sudo apt-get install -y git

# 작업 디렉토리 생성
mkdir -p /home/ubuntu/app
cd /home/ubuntu/app

# 필요한 파일 복사
# .env 파일은 별도로 생성 필요

echo "설치가 완료되었습니다. 시스템을 재시작하거나 새로운 세션을 시작하세요." 