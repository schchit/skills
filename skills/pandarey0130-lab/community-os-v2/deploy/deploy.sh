#!/bin/bash
#==============================================================================
# CommunityOS 一键部署脚本
# 支持: Ubuntu / Debian
# 依赖: pm2 (进程管理)
#==============================================================================
set -euo pipefail

# ── 颜色定义 ──────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'
BOLD='\033[1m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_ok()    { echo -e "${GREEN}[ OK ]${NC}  $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "${CYAN}[STEP]${NC}  $1"; }

# ── 变量 ──────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON_BIN=""
PM2_SCRIPT="$SCRIPT_DIR/ecosystem.config.js"
ACTION="${1:-install}"

# ── 工具函数 ──────────────────────────────────────────────────────────────
cmd_exists() { command -v "$1" &>/dev/null; }

detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS_ID="$ID"
        OS_NAME="$NAME"
        OS_VER="$VERSION_ID"
    else
        log_error "无法识别操作系统"
        exit 1
    fi

    if [[ "$OS_ID" == "ubuntu" ]] || [[ "$OS_ID" == "debian" ]] || [[ "$OS_ID" =~ ^(linuxmint|pop|elementary)$ ]]; then
        log_info "检测到系统: ${BOLD}${OS_NAME} ${OS_VER}${NC}"
    else
        log_error "仅支持 Ubuntu/Debian，当前系统: ${OS_NAME}"
        exit 1
    fi
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        SUDO=""
    else
        SUDO="sudo"
        log_info "需要 sudo 权限，部分操作将提权执行"
    fi
}

install_system_deps() {
    log_step "安装系统依赖..."
    $SUDO apt-get update -qq
    $SUDO apt-get install -y -qq \
        python3 python3-pip python3-venv \
        git curl wget \
        build-essential python3-dev \
        2>/dev/null | grep -v "^$" || true
    log_ok "系统依赖安装完成"
}

setup_python() {
    log_step "配置 Python 环境..."

    if [[ -d "$VENV_DIR" ]]; then
        log_info "虚拟环境已存在: $VENV_DIR"
    else
        log_info "创建虚拟环境..."
        python3 -m venv "$VENV_DIR"
        log_ok "虚拟环境创建完成"
    fi

    PYTHON_BIN="$VENV_DIR/bin/python"
    PIP_BIN="$VENV_DIR/bin/pip"

    # 升级 pip
    "$PYTHON_BIN" -m pip install --upgrade pip -q
    log_ok "Python 版本: $($PYTHON_BIN --version)"
}

install_requirements() {
    log_step "安装 Python 依赖..."
    cd "$PROJECT_DIR"
    "$PYTHON_BIN" -m pip install --upgrade -r requirements.txt -q
    log_ok "依赖安装完成"
}

setup_env() {
    log_step "配置环境变量..."

    if [[ ! -f "$PROJECT_DIR/.env" ]]; then
        if [[ -f "$PROJECT_DIR/.env.example" ]]; then
            cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
            log_ok "已从 .env.example 创建 .env"
            log_warn "请编辑 .env 填入实际配置:"
            log_warn "  nano $PROJECT_DIR/.env"
        else
            log_error ".env.example 不存在，请手动创建 .env 文件"
            exit 1
        fi
    else
        log_ok ".env 已存在，跳过"
    fi
}

init_knowledge_base() {
    log_step "初始化知识库索引..."
    cd "$PROJECT_DIR"

    # 创建 knowledge 目录（如果不存在）
    mkdir -p "$PROJECT_DIR/knowledge"
    mkdir -p "$PROJECT_DIR/knowledge_base/chroma_db"

    # 运行索引器
    if "$PYTHON_BIN" -m knowledge_base.indexer 2>&1 | tee /tmp/cos-index.log; then
        log_ok "知识库索引完成"
    else
        log_warn "知识库索引可能有警告，请检查 /tmp/cos-index.log"
    fi
}

install_pm2() {
    log_step "安装 / 检查 pm2..."

    if cmd_exists pm2; then
        PM2_VER=$(pm2 --version 2>/dev/null || echo "unknown")
        log_ok "pm2 已安装: v$PM2_VER"
        return
    fi

    log_info "安装 pm2..."
    $SUDO npm install -g pm2 --silent 2>/dev/null || \
        (curl -sL https://rpm.nodesource.com/setup_20.x | $SUDO bash - && \
         $SUDO apt-get install -y nodejs && \
         $SUDO npm install -g pm2) > /dev/null 2>&1

    if cmd_exists pm2; then
        log_ok "pm2 安装完成"
    else
        log_error "pm2 安装失败，请手动安装: npm install -g pm2"
        exit 1
    fi
}

generate_pm2_config() {
    log_step "生成 pm2 生态系统配置..."

    if [[ ! -f "$PM2_SCRIPT" ]]; then
        cat > "$PM2_SCRIPT" << 'PM2CFG'
// CommunityOS pm2 生态系统配置
// 自动生成 by deploy/deploy.sh

module.exports = {
  apps: [
    {
      name: 'communityos-admin',
      script: 'venv312/bin/python',
      args: '-m admin.app',
      cwd: __dirname + '/..',
      interpreter: 'none',
      env: {
        ADMIN_PORT: process.env.ADMIN_PORT || '8080',
      },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      restart_delay: 4000,
      exp_backoff_restart_delay: 100,
      error_file: 'logs/admin-err.log',
      out_file: 'logs/admin-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      kill_timeout: 5000,
    },
    {
      name: 'communityos-bot',
      script: 'venv312/bin/python',
      args: '-m bot_engine.manager',
      cwd: __dirname + '/..',
      interpreter: 'none',
      env: {
        TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN || '',
      },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      restart_delay: 4000,
      exp_backoff_restart_delay: 100,
      error_file: 'logs/bot-err.log',
      out_file: 'logs/bot-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      kill_timeout: 5000,
    },
  ],
};
PM2CFG
        log_ok "ecosystem.config.js 已生成"
    else
        log_ok "ecosystem.config.js 已存在，跳过"
    fi

    # 创建日志目录
    mkdir -p "$PROJECT_DIR/logs"
}

start_services() {
    log_step "启动服务..."

    # 加载环境变量
    if [[ -f "$PROJECT_DIR/.env" ]]; then
        set -a
        source "$PROJECT_DIR/.env"
        set +a
    fi

    cd "$PROJECT_DIR"

    # 启动
    if pm2 start "$PM2_SCRIPT" --env production; then
        log_ok "服务启动完成"
    else
        log_error "服务启动失败，请检查配置"
        exit 1
    fi

    # 保存 pm2 进程列表
    pm2 save
    # 设置开机自启
    pm2 startup 2>/dev/null || true
}

stop_services() {
    log_info "停止所有 CommunityOS 服务..."
    cd "$PROJECT_DIR"
    pm2 delete all 2>/dev/null || true
    log_ok "服务已停止"
}

restart_services() {
    log_info "重启所有 CommunityOS 服务..."
    cd "$PROJECT_DIR"
    if [[ -f "$PROJECT_DIR/.env" ]]; then
        set -a
        source "$PROJECT_DIR/.env"
        set +a
    fi
    pm2 restart all
    log_ok "服务已重启"
}

show_status() {
    log_step "服务状态:"
    cd "$PROJECT_DIR"
    echo ""
    pm2 list
    echo ""
    if [[ -f "$PROJECT_DIR/.env" ]]; then
        source "$PROJECT_DIR/.env"
    fi
    ADMIN_HOST="${ADMIN_HOST:-0.0.0.0}"
    ADMIN_PORT="${ADMIN_PORT:-8080}"
    log_info "管理后台: http://${ADMIN_HOST}:${ADMIN_PORT}"
    echo ""
}

show_logs() {
    local app="${2:-all}"
    local lines="${3:-50}"
    if [[ "$app" == "all" ]]; then
        pm2 logs --nostream --lines "$lines"
    else
        pm2 logs "$app" --nostream --lines "$lines"
    fi
}

# ── 帮助 ──────────────────────────────────────────────────────────────────
show_help() {
    cat << EOF
${BOLD}CommunityOS 部署脚本${NC}

${BOLD}用法:${NC}
    ./deploy.sh [命令]

${BOLD}命令:${NC}
    install     安装所有依赖并启动服务（默认）
    start       启动服务
    stop        停止服务
    restart     重启服务
    status      查看服务状态
    logs [app]  查看日志（可选：指定 app 名称）
    init        仅初始化（安装依赖 + 配置）
    help        显示帮助

${BOLD}示例:${NC}
    ./deploy.sh install   # 首次安装
    ./deploy.sh status    # 查看状态
    ./deploy.sh logs      # 查看所有日志
    ./deploy.sh logs bot  # 仅查看 bot 日志

EOF
}

# ── 主流程 ────────────────────────────────────────────────────────────────
main() {
    echo ""
    echo "=========================================="
    echo -e "  ${BOLD}CommunityOS${NC} 一键部署脚本"
    echo "=========================================="
    echo ""

    case "$ACTION" in
        install)
            detect_os
            check_root
            install_system_deps
            setup_python
            install_requirements
            setup_env
            install_pm2
            generate_pm2_config
            init_knowledge_base
            start_services
            echo ""
            echo "=========================================="
            echo -e "  ${GREEN}${BOLD}部署完成！${NC}"
            echo "=========================================="
            show_status
            echo -e "${YELLOW}查看日志: ./deploy.sh logs${NC}"
            echo -e "${YELLOW}重启服务: ./deploy.sh restart${NC}"
            echo ""
            ;;
        start)
            detect_os
            install_pm2
            start_services
            show_status
            ;;
        stop)
            stop_services
            ;;
        restart)
            detect_os
            install_pm2
            restart_services
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$@"
            ;;
        init)
            detect_os
            check_root
            install_system_deps
            setup_python
            install_requirements
            setup_env
            generate_pm2_config
            init_knowledge_base
            log_ok "初始化完成"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $ACTION"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
