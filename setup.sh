#!/bin/bash

# 시스템 업데이트
sudo apt-get update
sudo apt-get upgrade -y

# 필요한 패키지 설치
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Docker 저장소 추가
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker 설치
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# ubuntu 사용자를 docker 그룹에 추가
sudo usermod -aG docker ubuntu

# 작업 디렉토리 생성
mkdir -p /home/ubuntu/app

# SSH 키 설정
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

echo "설치가 완료되었습니다. 시스템을 재시작하거나 새로운 세션을 시작하세요." 