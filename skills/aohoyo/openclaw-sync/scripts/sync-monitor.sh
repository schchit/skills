#!/bin/bash

# OpenClaw 实时同步监控脚本
# 使用 inotify 实现文件变化实时同步

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE_DIR="/home/node/.openclaw/workspace"
RCLONE_CONF="$SKILL_DIR/config/rclone.conf"
BACKUP_CONF="$SKILL_DIR/config/backup.json"
SYNC_LIST="$SKILL_DIR/data/sync-list.txt"
LAST_SYNC_FILE="$SKILL_DIR/.last-sync"
DEBOUNCE_SECONDS=5

# 检查依赖
if ! command -v inotifywait &> /dev/null; then
    echo -e "${RED}错误: inotifywait 未安装${NC}"
    echo "请安装 inotify-tools: apt-get install inotify-tools"
    exit 1
fi

if ! command -v rclone &> /dev/null; then
    echo -e "${RED}错误: rclone 未安装${NC}"
    exit 1
fi

# 读取配置
if [ -f "$BACKUP_CONF" ]; then
    bucket=$(python3 "$SCRIPT_DIR/read-json.py" "$BACKUP_CONF" bucket 2>/dev/null || echo "")
    prefix=$(python3 "$SCRIPT_DIR/read-json.py" "$BACKUP_CONF" prefix 2>/dev/null || echo "")
    provider=$(python3 "$SCRIPT_DIR/read-json.py" "$BACKUP_CONF" providerName 2>/dev/null || echo "unknown")
else
    echo -e "${RED}错误: 配置文件不存在 $BACKUP_CONF${NC}"
    exit 1
fi

remote_path="openclaw-backup:$bucket/$prefix"

# 同步标志（防抖）
sync_pending=false
sync_timer_pid=""

# 执行同步
perform_sync() {
    local reason="$1"
    sync_pending=false
    
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] 🔄 开始同步 - $reason${NC}"
    
    if rclone sync "$WORKSPACE_DIR/" "$remote_path" \
        --include-from "$SYNC_LIST" \
        --config "$RCLONE_CONF" \
        --log-level INFO \
        --stats-one-line \
        --stats 5s 2>&1 | while read line; do
            echo -e "${BLUE}[rclone]${NC} $line"
        done; then
        
        echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 同步完成${NC}"
        touch "$LAST_SYNC_FILE"
    else
        echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 同步失败${NC}"
    fi
}

# 防抖同步（避免频繁触发）
schedule_sync() {
    local reason="$1"
    
    # 取消之前的定时器
    if [ -n "$sync_timer_pid" ] && kill -0 "$sync_timer_pid" 2>/dev/null; then
        kill "$sync_timer_pid" 2>/dev/null
    fi
    
    sync_pending=true
    
    # 设置新的定时器
    (
        sleep "$DEBOUNCE_SECONDS"
        if [ "$sync_pending" = true ]; then
            perform_sync "$reason"
        fi
    ) &
    sync_timer_pid=$!
}

# 启动信息
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   OpenClaw 实时同步监控服务                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}云服务商:${NC} $provider"
echo -e "${BLUE}存储桶:${NC} $bucket"
echo -e "${BLUE}实例:${NC} $prefix"
echo -e "${BLUE}监控目录:${NC} $WORKSPACE_DIR"
echo -e "${BLUE}防抖时间:${NC} ${DEBOUNCE_SECONDS}秒"
echo -e "${BLUE}同步列表:${NC} $SYNC_LIST"
echo ""
echo -e "${GREEN}🟢 服务已启动，正在监控文件变化...${NC}"
echo ""

# 首次同步
if [ ! -f "$LAST_SYNC_FILE" ]; then
    perform_sync "首次同步"
fi

# 使用 inotify 监控文件变化
# -r: 递归监控
# -m: 持续监控
# -e: 监控事件（修改、创建、删除、移动）
inotifywait -m -r \
    -e modify,create,delete,move,attrib \
    --exclude '(.git|.last-sync|node_modules)' \
    "$WORKSPACE_DIR" \
    2>/dev/null | while read path action file; do
    
    # 检查文件是否在同步列表中
    rel_path="${path#$WORKSPACE_DIR/}$file"
    
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] 📡 检测到变化: $action → $rel_path${NC}"
    
    # 触发防抖同步
    schedule_sync "文件变化: $rel_path"
done
