#!/bin/bash

# 启动实时监控同步服务（Docker 容器环境）

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="/home/node/.openclaw/workspace/skills/openclaw-sync/scripts"
PID_FILE="/tmp/openclaw-sync.pid"
LOG_FILE="/var/log/openclaw-sync.log"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════╗"
echo "║   OpenClaw 实时监控同步服务              ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# 检查是否已经在运行
if [ -f "$PID_FILE" ]; then
    old_pid=$(cat "$PID_FILE")
    if ps -p "$old_pid" > /dev/null 2>&1; then
        echo "⚠️  服务已在运行中 (PID: $old_pid)"
        echo ""
        echo "查看状态: ps -p $old_pid"
        echo "查看日志: tail -f $LOG_FILE"
        echo "停止服务: kill $old_pid"
        exit 0
    fi
fi

# 启动监控脚本（后台运行）
echo "启动实时监控..."
nohup bash "$SCRIPT_DIR/sync-monitor.sh" > "$LOG_FILE" 2>&1 &
new_pid=$!

# 保存 PID
echo $new_pid > "$PID_FILE"

echo -e "${GREEN}✅ 服务已启动${NC}"
echo ""
echo "服务信息:"
echo "  PID: $new_pid"
echo "  日志: $LOG_FILE"
echo "  PID 文件: $PID_FILE"
echo ""
echo "管理命令:"
echo "  查看状态: ps -p $new_pid"
echo "  查看日志: tail -f $LOG_FILE"
echo "  停止服务: kill $new_pid"
