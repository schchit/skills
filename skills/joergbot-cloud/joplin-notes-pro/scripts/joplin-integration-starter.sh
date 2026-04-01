#!/bin/bash
# Joplin Integration Starter Script
# Setup integrations between Joplin and other OpenClaw skills

set -e

# Source the check script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/joplin-check.sh"

# Configuration
INTEGRATION_DIR="${JOPLIN_INTEGRATION_DIR:-$HOME/.joplin-integrations}"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Help function
show_help() {
    cat << EOF
Joplin Integration Starter Script
Setup integrations between Joplin and other OpenClaw skills.

Usage: $0 [OPTIONS]

Options:
  -l, --list              List available integrations
  -s, --setup INTEGRATION Setup specific integration
  -a, --setup-all         Setup all integrations
  -t, --test INTEGRATION  Test specific integration
  -T, --test-all          Test all integrations
  -c, --clean             Clean integration directory
  -d, --dir DIR           Integration directory (default: ~/.joplin-integrations)
  -q, --quiet             Quiet mode
  -h, --help              Show this help message

Available Integrations:
  gmail           Save Gmail emails as Joplin notes
  calendar        Save calendar events as Joplin notes
  web-fetch       Save web articles as Joplin notes
  weather         Save weather reports as Joplin notes
  bitwarden       Save password documentation as notes
  daily-briefing  Create daily briefing from multiple sources
  weekly-summary  Create weekly summary notes

Examples:
  $0 --list                      # List available integrations
  $0 --setup gmail               # Setup Gmail integration
  $0 --setup-all                 # Setup all integrations
  $0 --test gmail                # Test Gmail integration
  $0 --clean                     # Clean integration files

Environment Variables:
  JOPLIN_INTEGRATION_DIR  Integration directory
  GOG_ACCOUNT             Gmail account for Gmail integration
  TELEGRAM_BOT_TOKEN      Telegram bot token for notifications
  TELEGRAM_CHAT_ID        Telegram chat ID for notifications

EOF
}

# Integration definitions
declare -A INTEGRATIONS=(
    ["gmail"]="Save Gmail emails as Joplin notes"
    ["calendar"]="Save calendar events as Joplin notes"
    ["web-fetch"]="Save web articles as Joplin notes"
    ["weather"]="Save weather reports as Joplin notes"
    ["bitwarden"]="Save password documentation as notes"
    ["daily-briefing"]="Create daily briefing from multiple sources"
    ["weekly-summary"]="Create weekly summary notes"
)

# Create integration directory
create_integration_dir() {
    if [ ! -d "$INTEGRATION_DIR" ]; then
        mkdir -p "$INTEGRATION_DIR"
        mkdir -p "$INTEGRATION_DIR/scripts"
        mkdir -p "$INTEGRATION_DIR/config"
        mkdir -p "$INTEGRATION_DIR/logs"
        
        log_success "Created integration directory: $INTEGRATION_DIR"
    fi
}

# List available integrations
list_integrations() {
    echo -e "${PURPLE}📦 Available Joplin Integrations${NC}"
    echo "=========================================="
    
    for integration in "${!INTEGRATIONS[@]}"; do
        local status="❌ Not installed"
        local config_file="$INTEGRATION_DIR/config/${integration}.conf"
        
        if [ -f "$config_file" ]; then
            status="✅ Installed"
        fi
        
        printf "%-20s %-40s %s\n" "$integration" "${INTEGRATIONS[$integration]}" "$status"
    done
    
    echo ""
    echo -e "${BLUE}💡 Usage:${NC}"
    echo "  $0 --setup <integration>    # Setup specific integration"
    echo "  $0 --setup-all              # Setup all integrations"
    echo "  $0 --test <integration>     # Test integration"
}

# Setup integration template
setup_integration_template() {
    local integration="$1"
    local description="$2"
    
    echo -e "${PURPLE}🔧 Setting up $integration → Joplin Integration${NC}"
    echo -e "${BLUE}Description:${NC} $description"
    
    create_integration_dir
    
    local config_file="$INTEGRATION_DIR/config/${integration}.conf"
    
    # Create configuration
    cat > "$config_file" << EOF
# $integration → Joplin Integration Configuration
# Created: $(date)
# Description: $description

# Joplin settings
JOPLIN_NOTEBOOK="${integration^}"  # Capitalized integration name
JOPLIN_TAGS="$integration,auto-saved"

# Sync settings
LAST_SYNC_FILE="\$INTEGRATION_DIR/last_${integration}_sync.txt"
SYNC_INTERVAL_HOURS=24

# Integration-specific settings
# Configure these based on your needs
EOF
    
    # Create simple script
    cat > "$INTEGRATION_DIR/scripts/${integration}-to-joplin.sh" << EOF
#!/bin/bash
# $integration to Joplin integration script

set -e

# Load configuration
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="\$SCRIPT_DIR/../config/${integration}.conf"
if [ -f "\$CONFIG_FILE" ]; then
    source "\$CONFIG_FILE"
else
    echo "Configuration file not found: \$CONFIG_FILE"
    exit 1
fi

# Source Joplin check script
JOPLIN_SKILL_DIR="\$HOME/.openclaw/workspace/skills/joplin-cli"
if [ -f "\$JOPLIN_SKILL_DIR/scripts/joplin-check.sh" ]; then
    source "\$JOPLIN_SKILL_DIR/scripts/joplin-check.sh"
else
    echo "Joplin skill not found"
    exit 1
fi

# Check last sync time
should_sync() {
    if [ ! -f "\$LAST_SYNC_FILE" ]; then
        return 0
    fi
    
    local last_sync=\$(cat "\$LAST_SYNC_FILE")
    local current_time=\$(date +%s)
    local hours_since=\$(( (current_time - last_sync) / 3600 ))
    
    [ \$hours_since -ge \$SYNC_INTERVAL_HOURS ]
}

# Main function
main() {
    echo "Starting $integration → Joplin sync..."
    
    # Check if we should sync
    if ! should_sync; then
        echo "Sync not needed yet (interval: \${SYNC_INTERVAL_HOURS}h)"
        return 0
    fi
    
    # Check Joplin health
    if ! check_joplin_health > /dev/null 2>&1; then
        echo "Joplin health check failed"
        return 1
    fi
    
    # TODO: Implement $integration specific logic here
    echo "This is a template for $integration integration."
    echo "Implement the actual integration logic here."
    
    # Example: Create a test note
    "\$JOPLIN_SKILL_DIR/scripts/joplin-quick-note.sh" \
        --quiet \
        --title "$integration Test \$(date '+%Y-%m-%d %H:%M')" \
        --notebook "\$JOPLIN_NOTEBOOK" \
        --tags "\$JOPLIN_TAGS" \
        "This is a test note from $integration integration."
    
    # Update last sync time
    date +%s > "\$LAST_SYNC_FILE"
    
    echo "$integration sync completed (test note created)"
    
    # Sync Joplin
    joplin sync > /dev/null 2>&1 && echo "Joplin sync completed" || echo "Joplin sync had issues"
}

# Run main
main "\$@"
EOF
    
    chmod +x "$INTEGRATION_DIR/scripts/${integration}-to-joplin.sh"
    
    log_success "$integration integration setup complete"
    echo -e "${BLUE}Configuration:${NC} $config_file"
    echo -e "${BLUE}Script:${NC} $INTEGRATION_DIR/scripts/${integration}-to-joplin.sh"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Edit $config_file to configure the integration"
    echo "2. Implement the actual logic in $INTEGRATION_DIR/scripts/${integration}-to-joplin.sh"
    echo "3. Run test: $0 --test $integration"
    echo "4. Add to cron for automatic sync"
}

# Test integration
test_integration() {
    local integration="$1"
    local script_file="$INTEGRATION_DIR/scripts/${integration}-to-joplin.sh"
    
    if [ ! -f "$script_file" ]; then
        log_error "Integration not found: $integration"
        log_error "Run '$0 --setup $integration' first"
        return 1
    fi
    
    echo -e "${PURPLE}🧪 Testing $integration Integration${NC}"
    
    # Run the integration script
    if "$script_file"; then
        log_success "✅ $integration integration test PASSED"
    else
        log_error "❌ $integration integration test FAILED"
        return 1
    fi
}

# Clean integration directory
clean_integration_dir() {
    if [ -d "$INTEGRATION_DIR" ]; then
        echo -e "${YELLOW}⚠ Cleaning integration directory: $INTEGRATION_DIR${NC}"
        rm -rf "$INTEGRATION_DIR"
        log_success "Integration directory cleaned"
    else
        log_info "Integration directory does not exist: $INTEGRATION_DIR"
    fi
}

# Parse arguments
parse_args() {
    local action=""
    local integration=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -l|--list)
                action="list"
                shift
                ;;
            -s|--setup)
                integration="$2"
                action="setup"
                shift 2
                ;;
            -a|--setup-all)
                action="setup-all"
                shift
                ;;
            -t|--test)
                integration="$2"
                action="test"
                shift 2
                ;;
            -T|--test-all)
                action="test-all"
                shift
                ;;
            -c|--clean)
                action="clean"
                shift
                ;;
            -d|--dir)
                INTEGRATION_DIR="$2"
                shift 2
                ;;
            -q|--quiet)
                # Quiet mode - suppress most output
                exec >/dev/null 2>&1
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Execute action
    case "$action" in
        list)
            list_integrations
            ;;
        setup)
            if [ -z "$integration" ]; then
                log_error "Integration name required for --setup"
                show_help
                exit 1
            fi
            
            if [ -z "${INTEGRATIONS[$integration]}" ]; then
                log_error "Unknown integration: $integration"
                list_integrations
                exit 1
            fi
            
            setup_integration_template "$integration" "${INTEGRATIONS[$integration]}"
            ;;
        setup-all)
            for integration in "${!INTEGRATIONS[@]}"; do
                setup_integration_template "$integration" "${INTEGRATIONS[$integration]}"
                echo ""
            done
            ;;
        test)
            if [ -z "$integration" ]; then
                log_error "Integration name required for --test"
                show_help
                exit 1
            fi
            
            test_integration "$integration"
            ;;
        test-all)
            for integration in "${!INTEGRATIONS[@]}"; do
                if [ -f "$INTEGRATION_DIR/scripts/${integration}-to-joplin.sh" ]; then
                    test_integration "$integration"
                    echo ""
                fi
            done
            ;;
        clean)
            clean_integration_dir
            ;;
        "")
            # No action specified, show help
            show_help
            ;;
    esac
}

# Main function
main() {
    # Check Joplin health first
    if ! check_joplin_health > /dev/null 2>&1; then
        log_error "Joplin health check failed. Please fix Joplin installation."
        exit 1
    fi
    
    parse_args "$@"
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi