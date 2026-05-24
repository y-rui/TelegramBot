#!/usr/bin/env bash
set -euo pipefail

# Telegram Bot Gateway 部署脚本
# 用法: ./deploy.sh [docker|systemd|direct]

PROJECT_DIR="/opt/telegram-bot"
METHOD="${1:-docker}"

echo "=== Telegram Bot Gateway 部署 ==="
echo "部署方式: $METHOD"

deploy_docker() {
    echo "--- Docker Compose 部署 ---"
    if ! command -v docker &>/dev/null; then
        echo "请先安装 Docker: curl -fsSL https://get.docker.com | sh"
        exit 1
    fi

    sudo mkdir -p "$PROJECT_DIR"
    sudo cp -r ./* "$PROJECT_DIR/"
    sudo cp .env "$PROJECT_DIR/" 2>/dev/null || {
        echo "未找到 .env，请从 .env.example 创建: cp .env.example .env"
        exit 1
    }

    cd "$PROJECT_DIR"
    sudo docker compose up -d --build
    echo "部署完成！服务运行在 http://<服务器IP>:8000"
    echo "健康检查: curl http://localhost:8000/webhook/health"
}

deploy_systemd() {
    echo "--- systemd 部署 ---"
    sudo mkdir -p "$PROJECT_DIR"
    sudo cp -r ./* "$PROJECT_DIR/"
    sudo cp .env "$PROJECT_DIR/" 2>/dev/null || {
        echo "未找到 .env，请生成"
        exit 1
    }

    cd "$PROJECT_DIR"
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt

    sudo cp telegram-bot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable telegram-bot
    sudo systemctl start telegram-bot
    echo "部署完成！查看状态: sudo systemctl status telegram-bot"
}

deploy_direct() {
    echo "--- 直接运行（测试用） ---"
    pip install -r requirements.txt
    python main.py
}

case "$METHOD" in
    docker)   deploy_docker ;;
    systemd)  deploy_systemd ;;
    direct)   deploy_direct ;;
    *)
        echo "用法: ./deploy.sh [docker|systemd|direct]"
        exit 1
        ;;
esac
