#!/bin/bash
# Joplin installation check script
# Usage: source this script or call functions directly

set -e

JOPLIN_CHECK_DEBUG=${JOPLIN_CHECK_DEBUG:-false}

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

debug_log() {
    if [ "$JOPLIN_CHECK_DEBUG" = "true" ]; then
        echo -e "${YELLOW}[DEBUG]${NC} $1"
    fi
}

# Check if Joplin CLI is installed
check_joplin_installed() {
    debug_log "Checking if Joplin CLI is installed..."
    
    if command -v joplin &> /dev/null; then
        log_success "Joplin CLI found: $(command -v joplin)"
        return 0
    else
        log_error "Joplin CLI not found in PATH"
        return 1
    fi
}

# Get Joplin version
get_joplin_version() {
    if check_joplin_installed; then
        local version_output
        version_output=$(joplin version 2>/dev/null | head -1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' || echo "unknown")
        echo "$version_output"
    else
        echo "not-installed"
    fi
}

# Check Joplin version compatibility
check_joplin_version() {
    local min_version="${1:-3.5.0}"
    local current_version
    
    current_version=$(get_joplin_version)
    
    if [ "$current_version" = "not-installed" ]; then
        log_error "Joplin is not installed"
        return 1
    fi
    
    debug_log "Current Joplin version: $current_version, Minimum required: $min_version"
    
    # Simple version comparison
    if [ "$(printf '%s\n' "$min_version" "$current_version" | sort -V | head -1)" = "$min_version" ]; then
        log_success "Joplin version $current_version meets minimum requirement $min_version"
        return 0
    else
        log_error "Joplin version $current_version is below minimum requirement $min_version"
        return 1
    fi
}

# Check Joplin configuration
check_joplin_config() {
    debug_log "Checking Joplin configuration..."
    
    if ! check_joplin_installed; then
        return 1
    fi
    
    # Check if Joplin is configured (has a profile)
    if joplin config 2>&1 | grep -q "No such file or directory"; then
        log_warning "Joplin is not configured. Run 'joplin' to initialize."
        return 1
    fi
    
    log_success "Joplin is configured"
    return 0
}

# Check sync configuration
check_joplin_sync() {
    debug_log "Checking Joplin sync configuration..."
    
    if ! check_joplin_config; then
        return 1
    fi
    
    local sync_target
    sync_target=$(joplin config sync.target 2>/dev/null || echo "0")
    
    if [ "$sync_target" = "0" ] || [ -z "$sync_target" ]; then
        log_warning "Joplin sync is not configured (sync.target = 0)"
        return 1
    fi
    
    log_success "Joplin sync is configured (sync.target = $sync_target)"
    return 0
}

# Check sync status
check_joplin_sync_status() {
    debug_log "Checking Joplin sync status..."
    
    if ! check_joplin_sync; then
        return 1
    fi
    
    local sync_status
    sync_status=$(joplin sync --status 2>/dev/null || echo "unknown")
    
    if echo "$sync_status" | grep -q "Last error"; then
        log_error "Joplin sync has errors: $sync_status"
        return 1
    elif echo "$sync_status" | grep -q "Last sync"; then
        log_success "Joplin sync is active"
        debug_log "Sync status: $sync_status"
        return 0
    else
        log_warning "Joplin sync status unknown"
        return 2
    fi
}

# Comprehensive Joplin health check
check_joplin_health() {
    local overall_status=0
    local errors=0
    local warnings=0
    
    log_info "Starting Joplin health check..."
    
    # 1. Check installation
    if check_joplin_installed; then
        log_success "✓ Joplin CLI is installed"
    else
        log_error "✗ Joplin CLI is not installed"
        errors=$((errors + 1))
        overall_status=1
    fi
    
    # 2. Check version
    if check_joplin_version "3.5.0"; then
        log_success "✓ Joplin version is compatible"
    else
        log_error "✗ Joplin version is incompatible"
        errors=$((errors + 1))
        overall_status=1
    fi
    
    # 3. Check configuration
    if check_joplin_config; then
        log_success "✓ Joplin is configured"
    else
        log_warning "⚠ Joplin is not configured (run 'joplin' to initialize)"
        warnings=$((warnings + 1))
        overall_status=2
    fi
    
    # 4. Check sync (optional but recommended)
    if check_joplin_sync; then
        log_success "✓ Joplin sync is configured"
        
        if check_joplin_sync_status; then
            log_success "✓ Joplin sync is active"
        else
            log_warning "⚠ Joplin sync has issues"
            warnings=$((warnings + 1))
            overall_status=2
        fi
    else
        log_warning "⚠ Joplin sync is not configured (recommended for backup)"
        warnings=$((warnings + 1))
        overall_status=2
    fi
    
    # Summary
    echo ""
    if [ $errors -gt 0 ]; then
        log_error "❌ Joplin health check FAILED ($errors errors, $warnings warnings)"
        return 1
    elif [ $warnings -gt 0 ]; then
        log_warning "⚠️  Joplin health check WARNING ($warnings warnings)"
        return 0  # Return 0 for warnings so scripts can continue
    else
        log_success "✅ Joplin health check PASSED"
        return 0
    fi
}

# Installation instructions
show_installation_instructions() {
    cat << EOF

📝 JOPLIN INSTALLATION INSTRUCTIONS

1. Install Node.js (if not already installed):
   - Ubuntu/Debian: sudo apt install nodejs npm
   - macOS: brew install node
   - Windows: Download from https://nodejs.org/

2. Install Joplin CLI globally:
   npm install -g joplin

3. Initialize Joplin:
   joplin

4. Configure sync (recommended):
   joplin config sync.target 10
   joplin config sync.10.path https://your-joplin-server.com
   joplin config sync.10.username your-username
   joplin config sync.10.password your-password

5. Verify installation:
   joplin version

For more information: https://joplinapp.org/help/
EOF
}

# Main execution
main() {
    local action="${1:-health}"
    
    case "$action" in
        installed)
            check_joplin_installed
            ;;
        version)
            get_joplin_version
            ;;
        config)
            check_joplin_config
            ;;
        sync)
            check_joplin_sync
            ;;
        sync-status)
            check_joplin_sync_status
            ;;
        health|check)
            check_joplin_health
            ;;
        install-help)
            show_installation_instructions
            ;;
        *)
            echo "Usage: $0 {health|installed|version|config|sync|sync-status|install-help}"
            exit 1
            ;;
    esac
}

# If script is executed directly, run main
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi

# Export functions for use in other scripts
export -f check_joplin_installed
export -f get_joplin_version
export -f check_joplin_version
export -f check_joplin_config
export -f check_joplin_sync
export -f check_joplin_sync_status
export -f check_joplin_health