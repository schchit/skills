#!/bin/bash

# 停止实时监控同步服务

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PID_FILE="/tmp/openclaw-sync.pid"

echo "╔══════════════════════════════════════════╗"
echo "║   停止 OpenClaw 实时监控同步服务         ║"
echo "╚══════════════════════════════════════════╝"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  服务未运行（PID 文件不存在）"
    exit 0
fi

pid=$(cat "$PID_FILE")

if ps -p "$pid" > /dev/null 2>&1; then
    echo "正在停止服务 (PID: $pid)..."
    kill "$pid"
    sleep 2
    
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "⚠️  强制停止..."
        kill -9 "$pid"
    fi
    
    rm -f "$PID_FILE"
    echo -e "${GREEN}✅ 服务已停止${NC}"
else
    echo "⚠️  服务未运行（PID: $pid 不存在）"
    rm -f "$PID_FILE"
fi
