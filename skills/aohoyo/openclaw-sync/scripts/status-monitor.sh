#!/bin/bash

# 查看实时监控同步服务状态

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PID_FILE="/tmp/openclaw-sync.pid"
LOG_FILE="/var/log/openclaw-sync.log"

echo "╔══════════════════════════════════════════╗"
echo "║   OpenClaw 实时监控同步服务状态          ║"
echo "╚══════════════════════════════════════════╝"

if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}状态: 未运行${NC}"
    echo "PID 文件不存在: $PID_FILE"
    exit 1
fi

pid=$(cat "$PID_FILE")

if ps -p "$pid" > /dev/null 2>&1; then
    echo -e "${GREEN}状态: 运行中${NC}"
    echo ""
    ps -p "$pid" -o pid,ppid,cmd,%cpu,%mem,etime
    echo ""
    echo "日志文件: $LOG_FILE"
    if [ -f "$LOG_FILE" ]; then
        echo "日志大小: $(du -h "$LOG_FILE" | cut -f1)"
        echo ""
        echo "最近 10 行日志:"
        tail -10 "$LOG_FILE"
    fi
else
    echo -e "${RED}状态: 已停止${NC}"
    echo "PID: $pid (进程不存在)"
fi
