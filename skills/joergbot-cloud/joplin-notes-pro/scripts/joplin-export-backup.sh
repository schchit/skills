#!/bin/bash
# Joplin Export Backup Script
# Backup all notes to Markdown files with metadata and optional encryption

set -e

# Source the check script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/joplin-check.sh"

# Default configuration
BACKUP_DIR="${JOPLIN_BACKUP_DIR:-$HOME/backups/joplin}"
BACKUP_FORMAT="${JOPLIN_BACKUP_FORMAT:-md}"  # md, jex, raw
COMPRESS="${JOPLIN_BACKUP_COMPRESS:-true}"
ENCRYPT="${JOPLIN_BACKUP_ENCRYPT:-false}"
ENCRYPT_PASSWORD="${JOPLIN_BACKUP_PASSWORD:-}"
KEEP_DAYS="${JOPLIN_BACKUP_KEEP_DAYS:-30}"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Help function
show_help() {
    cat << EOF
Joplin Export Backup Script
Backup all Joplin notes with metadata, compression, and optional encryption.

Usage: $0 [OPTIONS] [BACKUP_DIR]

Options:
  -d, --dir DIR          Backup directory (default: ~/backups/joplin)
  -f, --format FORMAT    Export format: md, jex, raw (default: md)
  -c, --compress         Compress backup (tar.gz) [default: true]
  -C, --no-compress      Don't compress backup
  -e, --encrypt          Encrypt backup with password
  -p, --password PASS    Encryption password (or use JOPLIN_BACKUP_PASSWORD)
  -k, --keep-days DAYS   Keep backups for N days (default: 30)
  -i, --include-metadata Include metadata JSON with backup
  -s, --sync-first       Sync Joplin before backup
  -t, --test             Test mode (don't actually export)
  -q, --quiet            Quiet mode (minimal output)
  -h, --help             Show this help message

Export Formats:
  md    Markdown files (readable, preserves formatting)
  jex   Joplin Export Format (includes everything)
  raw   Raw database export (fastest)

Examples:
  $0                                # Backup to default directory
  $0 /mnt/backup/joplin             # Backup to specific directory
  $0 -f jex -c -e -p "secret"       # Encrypted JEX backup
  $0 -k 7 --sync-first              # Keep 7 days, sync first
  $0 -t                             # Test mode (dry run)

Environment Variables:
  JOPLIN_BACKUP_DIR       Default backup directory
  JOPLIN_BACKUP_FORMAT    Default format (md, jex, raw)
  JOPLIN_BACKUP_COMPRESS  Compress backups (true/false)
  JOPLIN_BACKUP_ENCRYPT   Encrypt backups (true/false)
  JOPLIN_BACKUP_PASSWORD  Encryption password
  JOPLIN_BACKUP_KEEP_DAYS Keep backups for N days

EOF
}

# Parse command line arguments
parse_args() {
    local backup_dir=""
    local format="$BACKUP_FORMAT"
    local compress="$COMPRESS"
    local encrypt="$ENCRYPT"
    local password="$ENCRYPT_PASSWORD"
    local keep_days="$KEEP_DAYS"
    local include_metadata=false
    local sync_first=false
    local test_mode=false
    local quiet=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--dir)
                backup_dir="$2"
                shift 2
                ;;
            -f|--format)
                format="$2"
                case "$format" in
                    md|jex|raw) ;;
                    *) log_error "Invalid format: $format. Use: md, jex, raw"
                       exit 1 ;;
                esac
                shift 2
                ;;
            -c|--compress)
                compress=true
                shift
                ;;
            -C|--no-compress)
                compress=false
                shift
                ;;
            -e|--encrypt)
                encrypt=true
                shift
                ;;
            -p|--password)
                password="$2"
                shift 2
                ;;
            -k|--keep-days)
                keep_days="$2"
                if ! [[ "$keep_days" =~ ^[0-9]+$ ]]; then
                    log_error "Invalid days: $keep_days. Must be a number."
                    exit 1
                fi
                shift 2
                ;;
            -i|--include-metadata)
                include_metadata=true
                shift
                ;;
            -s|--sync-first)
                sync_first=true
                shift
                ;;
            -t|--test)
                test_mode=true
                shift
                ;;
            -q|--quiet)
                quiet=true
                shift
                ;;
            --)
                shift
                break
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                # Assume it's the backup directory
                backup_dir="$1"
                shift
                ;;
        esac
    done
    
    # Set backup directory
    if [ -n "$backup_dir" ]; then
        BACKUP_DIR="$backup_dir"
    fi
    
    # Validate encryption
    if [ "$encrypt" = true ] && [ -z "$password" ]; then
        log_error "Encryption requires a password. Use --password or set JOPLIN_BACKUP_PASSWORD."
        exit 1
    fi
    
    # Return values
    ARG_DIR="$BACKUP_DIR"
    ARG_FORMAT="$format"
    ARG_COMPRESS="$compress"
    ARG_ENCRYPT="$encrypt"
    ARG_PASSWORD="$password"
    ARG_KEEP_DAYS="$keep_days"
    ARG_METADATA="$include_metadata"
    ARG_SYNC="$sync_first"
    ARG_TEST="$test_mode"
    ARG_QUIET="$quiet"
}

# Create backup directory
create_backup_dir() {
    local dir="$1"
    
    if [ ! -d "$dir" ]; then
        log_info "Creating backup directory: $dir"
        mkdir -p "$dir"
    fi
    
    # Check write permissions
    if [ ! -w "$dir" ]; then
        log_error "No write permission for directory: $dir"
        return 1
    fi
    
    echo "$dir"
}

# Generate backup filename
generate_backup_filename() {
    local format="$1"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    case "$format" in
        md) echo "joplin_backup_${timestamp}" ;;
        jex) echo "joplin_export_${timestamp}" ;;
        raw) echo "joplin_raw_${timestamp}" ;;
        *) echo "joplin_backup_${timestamp}" ;;
    esac
}

# Sync Joplin before backup
sync_joplin() {
    if [ "$ARG_QUIET" = false ]; then
        log_info "Syncing Joplin before backup..."
    fi
    
    joplin sync > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        if [ "$ARG_QUIET" = false ]; then
            log_success "Sync completed"
        fi
        return 0
    else
        log_warning "Sync had issues (continuing with local data)"
        return 1
    fi
}

# Export notes
export_notes() {
    local format="$1"
    local output_dir="$2"
    
    local export_cmd=""
    
    case "$format" in
        md)
            export_cmd="joplin export --format md \"$output_dir\""
            ;;
        jex)
            export_cmd="joplin export --format jex \"$output_dir/joplin_export.jex\""
            ;;
        raw)
            export_cmd="joplin export --format raw \"$output_dir\""
            ;;
    esac
    
    if [ "$ARG_QUIET" = false ]; then
        log_info "Exporting notes in $format format..."
    fi
    
    # Execute export
    eval "$export_cmd" 2>&1
    
    if [ $? -eq 0 ]; then
        if [ "$ARG_QUIET" = false ]; then
            log_success "Export completed"
        fi
        return 0
    else
        log_error "Export failed"
        return 1
    fi
}

# Create metadata file
create_metadata() {
    local output_dir="$1"
    local metadata_file="$output_dir/backup_metadata.json"
    
    local note_count=$(joplin ls | grep -c "^[a-f0-9]")
    local notebook_count=$(joplin ls | grep -c "^[A-Z]")
    local tag_count=$(joplin tag list | wc -l)
    local joplin_version=$(joplin version 2>/dev/null | head -1)
    local sync_status=$(joplin sync --status 2>/dev/null || echo "unknown")
    
    cat > "$metadata_file" << EOF
{
  "backup": {
    "timestamp": "$(date -Iseconds)",
    "format": "$ARG_FORMAT",
    "compressed": $ARG_COMPRESS,
    "encrypted": $ARG_ENCRYPT
  },
  "joplin": {
    "version": "$joplin_version",
    "note_count": $note_count,
    "notebook_count": $notebook_count,
    "tag_count": $tag_count,
    "sync_status": "$sync_status"
  },
  "system": {
    "hostname": "$(hostname)",
    "user": "$(whoami)",
    "backup_script_version": "1.0.0"
  }
}
EOF
    
    if [ "$ARG_QUIET" = false ]; then
        log_success "Metadata created: $metadata_file"
    fi
}

# Compress backup
compress_backup() {
    local source_dir="$1"
    local backup_name="$2"
    local output_file="$source_dir/../${backup_name}.tar.gz"
    
    if [ "$ARG_QUIET" = false ]; then
        log_info "Compressing backup..."
    fi
    
    # Create tar.gz
    tar -czf "$output_file" -C "$source_dir" . 2>/dev/null
    
    if [ $? -eq 0 ]; then
        local size=$(du -h "$output_file" | cut -f1)
        if [ "$ARG_QUIET" = false ]; then
            log_success "Compressed: $output_file ($size)"
        fi
        echo "$output_file"
        return 0
    else
        log_error "Compression failed"
        return 1
    fi
}

# Encrypt backup
encrypt_backup() {
    local input_file="$1"
    local password="$2"
    local output_file="${input_file}.gpg"
    
    if [ "$ARG_QUIET" = false ]; then
        log_info "Encrypting backup..."
    fi
    
    # Check if gpg is available
    if ! command -v gpg &> /dev/null; then
        log_error "GPG not found. Install with: sudo apt install gnupg"
        return 1
    fi
    
    # Encrypt with GPG
    gpg --batch --yes --passphrase "$password" --symmetric --cipher-algo AES256 -o "$output_file" "$input_file" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        if [ "$ARG_QUIET" = false ]; then
            log_success "Encrypted: $output_file"
        fi
        # Remove unencrypted file
        rm "$input_file"
        echo "$output_file"
        return 0
    else
        log_error "Encryption failed"
        return 1
    fi
}

# Clean old backups
clean_old_backups() {
    local backup_dir="$1"
    local keep_days="$2"
    
    if [ "$keep_days" -le 0 ]; then
        return 0
    fi
    
    if [ "$ARG_QUIET" = false ]; then
        log_info "Cleaning backups older than $keep_days days..."
    fi
    
    local deleted_count=0
    local current_time=$(date +%s)
    local cutoff_time=$((current_time - keep_days * 86400))
    
    # Find and delete old backup files
    find "$backup_dir" -name "joplin_*" -type f -mtime "+$keep_days" | while read -r file; do
        if [ "$ARG_QUIET" = false ]; then
            log_info "Deleting old backup: $(basename "$file")"
        fi
        rm "$file"
        deleted_count=$((deleted_count + 1))
    done
    
    if [ "$deleted_count" -gt 0 ] && [ "$ARG_QUIET" = false ]; then
        log_success "Cleaned $deleted_count old backups"
    fi
    
    return 0
}

# Main function
main() {
    parse_args "$@"
    
    # Check Joplin health (allow warnings for backup)
    if ! check_joplin_installed; then
        log_error "Joplin CLI not found. Please install Joplin first."
        exit 1
    fi
    
    # Display backup info
    if [ "$ARG_QUIET" = false ]; then
        echo -e "${PURPLE}💾 Joplin Backup${NC}"
        echo -e "${BLUE}Backup Directory:${NC} $ARG_DIR"
        echo -e "${BLUE}Format:${NC} $ARG_FORMAT"
        echo -e "${BLUE}Compress:${NC} $ARG_COMPRESS"
        echo -e "${BLUE}Encrypt:${NC} $ARG_ENCRYPT"
        echo -e "${BLUE}Keep Days:${NC} $ARG_KEEP_DAYS"
        echo -e "${BLUE}Test Mode:${NC} $ARG_TEST"
        echo ""
    fi
    
    # Test mode check
    if [ "$ARG_TEST" = true ]; then
        log_info "TEST MODE - No changes will be made"
        
        # Count notes
        local note_count=$(joplin ls | grep -c "^[a-f0-9]")
        local notebook_count=$(joplin ls | grep -c "^[A-Z]")
        
        echo -e "${GREEN}✅ Backup test successful${NC}"
        echo -e "${BLUE}Notes:${NC} $note_count"
        echo -e "${BLUE}Notebooks:${NC} $notebook_count"
        echo -e "${BLUE}Would backup to:${NC} $ARG_DIR"
        
        exit 0
    fi
    
    # Create backup directory
    backup_base_dir=$(create_backup_dir "$ARG_DIR")
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Generate backup name
    backup_name=$(generate_backup_filename "$ARG_FORMAT")
    backup_output_dir="$backup_base_dir/$backup_name"
    
    # Create specific backup directory
    mkdir -p "$backup_output_dir"
    
    # Sync if requested
    if [ "$ARG_SYNC" = true ]; then
        sync_joplin
    fi
    
    # Export notes
    if ! export_notes "$ARG_FORMAT" "$backup_output_dir"; then
        log_error "Backup failed during export"
        # Clean up failed backup directory
        rm -rf "$backup_output_dir"
        exit 1
    fi
    
    # Create metadata if requested
    if [ "$ARG_METADATA" = true ]; then
        create_metadata "$backup_output_dir"
    fi
    
    # Final backup file
    final_backup_file=""
    
    # Compress if requested
    if [ "$ARG_COMPRESS" = true ]; then
        compressed_file=$(compress_backup "$backup_output_dir" "$backup_name")
        if [ $? -eq 0 ]; then
            final_backup_file="$compressed_file"
            # Remove uncompressed directory
            rm -rf "$backup_output_dir"
        else
            log_warning "Compression failed, keeping uncompressed backup"
            final_backup_file="$backup_output_dir"
        fi
    else
        final_backup_file="$backup_output_dir"
    fi
    
    # Encrypt if requested
    if [ "$ARG_ENCRYPT" = true ] && [ -n "$ARG_PASSWORD" ]; then
        if [ -f "$final_backup_file" ]; then
            encrypted_file=$(encrypt_backup "$final_backup_file" "$ARG_PASSWORD")
            if [ $? -eq 0 ]; then
                final_backup_file="$encrypted_file"
            else
                log_warning "Encryption failed, keeping unencrypted backup"
            fi
        fi
    fi
    
    # Clean old backups
    clean_old_backups "$backup_base_dir" "$ARG_KEEP_DAYS"
    
    # Success message
    if [ "$ARG_QUIET" = false ]; then
        echo ""
        echo -e "${GREEN}✅ Backup completed successfully!${NC}"
        echo -e "${BLUE}Backup Location:${NC} $final_backup_file"
        
        # Show file info
        if [ -f "$final_backup_file" ]; then
            local size=$(du -h "$final_backup_file" 2>/dev/null | cut -f1 || echo "unknown")
            echo -e "${BLUE}Size:${NC} $size"
        elif [ -d "$final_backup_file" ]; then
            local size=$(du -sh "$final_backup_file" 2>/dev/null | cut -f1 || echo "unknown")
            echo -e "${BLUE}Size:${NC} $size (directory)"
        fi
        
        echo ""
        echo -e "${PURPLE}📊 Backup Summary${NC}"
        echo -e "${BLUE}Format:${NC} $ARG_FORMAT"
        echo -e "${BLUE}Compressed:${NC} $ARG_COMPRESS"
        echo -e "${BLUE}Encrypted:${NC} $ARG_ENCRYPT"
        echo -e "${BLUE}Timestamp:${NC} $(date)"
        
        # Count notes for summary
        local note_count=$(joplin ls | grep -c "^[a-f0-9]" 2>/dev/null || echo "unknown")
        echo -e "${BLUE}Notes Backed Up:${NC} $note_count"
        
        echo ""
        echo -e "${BLUE}💡 Tips:${NC}"
        echo "  • Restore backup: joplin import \"$final_backup_file\""
        echo "  • Schedule backups: Add to crontab"
        echo "  • Verify backup: Check file exists and size"
        
        # Crontab example
        echo ""
        echo -e "${YELLOW}📅 Crontab Example (daily at 2 AM):${NC}"
        echo "0 2 * * * $SCRIPT_DIR/joplin-export-backup.sh --quiet --sync-first --keep-days 30"
    else
        echo "$final_backup_file"
    fi
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi