#!/bin/bash
#
# Feishu Notifier Skill
# 飞书通知脚本
#
# 功能：通过飞书 Open API 发送即时通知消息

set -e

# ==================== 配置区域 ====================
FEISHU_APP_ID="${FEISHU_APP_ID:-your_app_id}"
FEISHU_APP_SECRET="${FEISHU_APP_SECRET:-your_app_secret}"
FEISHU_USER_ID="${FEISHU_USER_ID:-your_user_id}"

# 飞书 API 端点
FEISHU_API_BASE="https://open.feishu.cn/open-apis"
TOKEN_ENDPOINT="${FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
MESSAGE_ENDPOINT="${FEISHU_API_BASE}/im/v1/messages"

# ==================== 函数定义 ====================

show_help() {
    cat << EOF
Feishu Notifier - 飞书通知脚本

用法: $0 [选项] [消息内容]

选项:
    -h, --help          显示帮助信息
    -t, --title TITLE   设置消息标题
    -m, --message MSG   设置消息内容
    -u, --user USER_ID  指定接收用户ID
    --test              发送测试消息

环境变量:
    FEISHU_APP_ID       飞书应用 ID
    FEISHU_APP_SECRET   飞书应用密钥
    FEISHU_USER_ID      接收用户 Open ID

示例:
    $0 -t "任务完成" -m "备份任务已成功执行"
    echo "系统警告" | $0 -t "磁盘空间不足"
    $0 --test
EOF
}

# 获取访问令牌
get_access_token() {
    local response
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{\"app_id\":\"${FEISHU_APP_ID}\",\"app_secret\":\"${FEISHU_APP_SECRET}\"}" \
        "${TOKEN_ENDPOINT}")
    
    local code
    code=$(echo "$response" | grep -o '"code":[0-9]*' | cut -d':' -f2)
    
    if [ "$code" != "0" ]; then
        echo "错误：获取访问令牌失败" >&2
        echo "响应: $response" >&2
        return 1
    fi
    
    echo "$response" | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4
}

# 发送消息
send_message() {
    local token="$1"
    local title="$2"
    local content="$3"
    local user_id="${4:-$FEISHU_USER_ID}"
    
    # 构建消息卡片
    local message_card
    message_card=$(cat << EOF
{
    "receive_id": "${user_id}",
    "msg_type": "interactive",
    "content": "{\"card\":{\"config\":{\"wide_screen_mode\":true},\"header\":{\"title\":{\"tag\":\"plain_text\",\"content\":\"${title}\"},\"template\":\"blue\"},\"elements\":[{\"tag\":\"div\",\"text\":{\"tag\":\"lark_md\",\"content\":\"${content}\"}},{\"tag\":\"note\",\"elements\":[{\"tag\":\"plain_text\",\"content\":\"发送时间: $(date '+%Y-%m-%d %H:%M:%S')\"}]}]}}"
}
EOF
)
    
    local response
    response=$(curl -s -X POST \
        -H "Authorization: Bearer ${token}" \
        -H "Content-Type: application/json" \
        -d "$message_card" \
        "${MESSAGE_ENDPOINT}?receive_id_type=open_id")
    
    local code
    code=$(echo "$response" | grep -o '"code":[0-9]*' | cut -d':' -f2)
    
    if [ "$code" != "0" ]; then
        echo "错误：发送消息失败" >&2
        echo "响应: $response" >&2
        return 1
    fi
    
    echo "✓ 消息发送成功"
    return 0
}

# 发送测试消息
send_test_message() {
    local hostname
    hostname=$(hostname)
    local title="🧪 Feishu Notifier 测试消息"
    local content="**服务器**: ${hostname}  
**状态**: 配置正确，可以正常发送通知  
**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
    
    echo "正在发送测试消息到用户 ${FEISHU_USER_ID}..."
    
    local token
    token=$(get_access_token) || return 1
    send_message "$token" "$title" "$content"
}

# ==================== 主程序 ====================

main() {
    local title="系统通知"
    local message=""
    local user_id=""
    local test_mode=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--title)
                title="$2"
                shift 2
                ;;
            -m|--message)
                message="$2"
                shift 2
                ;;
            -u|--user)
                user_id="$2"
                shift 2
                ;;
            --test)
                test_mode=true
                shift
                ;;
            *)
                if [ -z "$message" ]; then
                    message="$1"
                else
                    message="${message} $1"
                fi
                shift
                ;;
        esac
    done
    
    # 检查必要的环境变量
    if [ "$FEISHU_APP_ID" = "your_app_id" ] || [ -z "$FEISHU_APP_ID" ]; then
        echo "错误：请设置 FEISHU_APP_ID 环境变量" >&2
        exit 1
    fi
    
    if [ "$FEISHU_APP_SECRET" = "your_app_secret" ] || [ -z "$FEISHU_APP_SECRET" ]; then
        echo "错误：请设置 FEISHU_APP_SECRET 环境变量" >&2
        exit 1
    fi
    
    if [ "$FEISHU_USER_ID" = "your_user_id" ] && [ -z "$user_id" ]; then
        echo "错误：请设置 FEISHU_USER_ID 环境变量或使用 -u 指定用户" >&2
        exit 1
    fi
    
    # 测试模式
    if [ "$test_mode" = true ]; then
        send_test_message
        exit $?
    fi
    
    # 从管道读取消息内容
    if [ -z "$message" ] && [ ! -t 0 ]; then
        message=$(cat)
    fi
    
    # 检查消息内容
    if [ -z "$message" ]; then
        echo "错误：消息内容不能为空" >&2
        show_help
        exit 1
    fi
    
    # 转义特殊字符用于 JSON
    message=$(echo "$message" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g')
    
    # 获取访问令牌并发送消息
    echo "正在发送通知..."
    local token
    token=$(get_access_token) || exit 1
    send_message "$token" "$title" "$message" "$user_id"
}

main "$@"
