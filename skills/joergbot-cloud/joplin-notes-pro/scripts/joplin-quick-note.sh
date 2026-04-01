#!/bin/bash
# Joplin Quick Note Script
# Create quick notes with optional tags and notebook assignment

set -e

# Don't source the check script - it causes TUI problems
# SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# source "$SCRIPT_DIR/joplin-check.sh"

# Default configuration
DEFAULT_NOTEBOOK="${JOPLIN_DEFAULT_NOTEBOOK:-Inbox}"
DEFAULT_TAGS="${JOPLIN_DEFAULT_TAGS:-quick-note}"
EDITOR="${EDITOR:-vi}"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
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
    if [ "${JOPLIN_CHECK_DEBUG:-false}" = "true" ]; then
        echo -e "${YELLOW}[DEBUG]${NC} $1"
    fi
}

# Help function
show_help() {
    cat << EOF
Joplin Quick Note Script
Create quick notes with optional tags and notebook assignment.

Usage: $0 [OPTIONS] "Note Title" "Note Content"

Options:
  -t, --tags TAG1,TAG2     Add tags to the note (comma-separated)
  -n, --notebook NAME      Place note in specific notebook
  -e, --edit               Open note in editor after creation
  -s, --sync               Sync after creating note
  -q, --quiet              Suppress output
  -h, --help               Show this help message

Environment Variables:
  JOPLIN_DEFAULT_NOTEBOOK  Default notebook (default: Inbox)
  JOPLIN_DEFAULT_TAGS      Default tags (default: quick-note)
  EDITOR                   Editor to use with --edit option

Examples:
  $0 "Meeting Notes" "Discussed project timeline"
  $0 -t "work,meeting" -n "Work" "Project Update" "Team decided on new deadline"
  $0 -e "Journal Entry" "Today I learned..."
  echo "Note content" | $0 "Piped Note"

EOF
}

# Parse command line arguments
parse_args() {
    local title=""
    local content=""
    local tags=""
    local notebook=""
    local do_edit=false
    local do_sync=false
    local quiet=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--tags)
                tags="$2"
                shift 2
                ;;
            -n|--notebook)
                notebook="$2"
                shift 2
                ;;
            -e|--edit)
                do_edit=true
                shift
                ;;
            -s|--sync)
                do_sync=true
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
                # First non-option argument is title, rest is content
                if [ -z "$title" ]; then
                    title="$1"
                else
                    # If content already has something, add space
                    if [ -n "$content" ]; then
                        content="$content $1"
                    else
                        content="$1"
                    fi
                fi
                shift
                ;;
        esac
    done
    
    # If we have remaining arguments after parsing, they're part of content
    while [[ $# -gt 0 ]]; do
        if [ -n "$content" ]; then
            content="$content $1"
        else
            content="$1"
        fi
        shift
    done
    
    # Check if content is coming from stdin
    if [ -z "$content" ] && ! tty -s; then
        content=$(cat -)
    fi
    
    # Validate required arguments
    if [ -z "$title" ]; then
        log_error "Note title is required"
        show_help
        exit 1
    fi
    
    if [ -z "$content" ] && [ "$do_edit" = false ]; then
        log_error "Note content is required (or use --edit to open editor)"
        show_help
        exit 1
    fi
    
    # Set defaults if not provided
    notebook="${notebook:-$DEFAULT_NOTEBOOK}"
    tags="${tags:-$DEFAULT_TAGS}"
    
    # Return values (using global variables in bash)
    ARG_TITLE="$title"
    ARG_CONTENT="$content"
    ARG_TAGS="$tags"
    ARG_NOTEBOOK="$notebook"
    ARG_EDIT="$do_edit"
    ARG_SYNC="$do_sync"
    ARG_QUIET="$quiet"
}

# Create notebook if it doesn't exist
ensure_notebook() {
    local notebook="$1"
    
    # Check if notebook exists
    if ! joplin_noninteractive ls "$notebook" 2>/dev/null | grep -q "Not found"; then
        debug_log "Notebook '$notebook' exists"
        return 0
    fi
    
    # Create notebook
    log_info "Creating notebook: $notebook"
    joplin_noninteractive mkbook "$notebook" > /dev/null 2>&1 || {
        log_error "Failed to create notebook: $notebook"
        return 1
    }
    
    log_success "Created notebook: $notebook"
    return 0
}

# Helper function for non-interactive Joplin calls
joplin_noninteractive() {
    # Use script to run Joplin without TUI
    script -q -c "joplin $*" /dev/null 2>&1
}

# Create the note
create_note() {
    local title="$1"
    local content="$2"
    local notebook="$3"
    local tags="$4"
    local do_edit="$5"
    
    local note_id=""
    
    # Create the note
    log_info "Creating note: $title"
    
    if [ "$do_edit" = true ]; then
        # Create note and open in editor
        joplin_noninteractive mknote "$title" > /dev/null 2>&1
        sleep 1
        # Get note ID from JSON
        local json_output=$(joplin_noninteractive ls --format json 2>/dev/null || echo "[]")
        note_id=$(echo "$json_output" | jq -r --arg title "$title" '.[] | select(.title == $title) | .id[0:5]' 2>/dev/null | head -1)
        
        if [ -z "$note_id" ]; then
            # Fallback to most recent note
            note_id=$(joplin_noninteractive ls -l | head -1 | awk '{print $1}')
        fi
        
        if [ -n "$note_id" ]; then
            # Open in editor
            log_info "Opening note in editor: $EDITOR"
            joplin_noninteractive edit "$note_id"
            
            # Get content after editing
            content=$(joplin_noninteractive cat "$note_id")
        else
            log_error "Failed to create note"
            return 1
        fi
    else
        # Create note with content
        debug_log "Creating note with title: $title"
        echo "$content" | joplin_noninteractive mknote "$title" > /dev/null 2>&1
        # Wait a moment for the note to be created
        sleep 1
        debug_log "Looking for note with title: $title"
        # Use JSON output to get full titles
        local json_output=$(joplin_noninteractive ls --format json 2>/dev/null || echo "[]")
        note_id=$(echo "$json_output" | jq -r --arg title "$title" '.[] | select(.title == $title) | .id[0:5]' 2>/dev/null | head -1)
        
        if [ -z "$note_id" ]; then
            # Fallback: get the most recent note (should be the one we just created)
            debug_log "JSON method failed, getting most recent note"
            note_id=$(joplin_noninteractive ls -l | head -1 | awk '{print $1}')
        fi
        
        debug_log "Found note ID: $note_id"
    fi
    
    if [ -z "$note_id" ]; then
        log_error "Failed to create note or get note ID"
        debug_log "Available notes (full list):"
        joplin_noninteractive ls -l
        return 1
    fi
    
    log_success "Created note with ID: $note_id"
    # Return clean note ID (without log messages)
    echo "$note_id" | tr -d '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
    
    # Move to notebook if specified and not already in Inbox
    if [ "$notebook" != "Inbox" ]; then
        log_info "Moving note to notebook: $notebook"
        ensure_notebook "$notebook"
        joplin_noninteractive mv "$note_id" "$notebook" > /dev/null 2>&1 || {
            log_warning "Failed to move note to notebook (note might already be there)"
        }
    fi
    
    # Add tags if specified
    if [ -n "$tags" ] && [ "$tags" != "none" ]; then
        IFS=',' read -ra tag_array <<< "$tags"
        for tag in "${tag_array[@]}"; do
            tag=$(echo "$tag" | xargs) # Trim whitespace
            if [ -n "$tag" ]; then
                log_info "Adding tag: $tag"
                joplin_noninteractive tag "$tag" "$note_id" > /dev/null 2>&1 || {
                    log_warning "Failed to add tag: $tag"
                }
            fi
        done
    fi
    
    echo "$note_id"
    return 0
}

# Main function
main() {
    parse_args "$@"
    
    debug_log "Starting main function with title: $ARG_TITLE"
    
    # Simple Joplin check instead of full health check
    if ! command -v joplin &> /dev/null; then
        log_error "Joplin CLI not found in PATH"
        exit 1
    fi
    
    debug_log "Joplin found in PATH"
    
    debug_log "Calling create_note with args: title=$ARG_TITLE, notebook=$ARG_NOTEBOOK, tags=$ARG_TAGS, edit=$ARG_EDIT"
    
    # Create the note
    note_id=$(create_note "$ARG_TITLE" "$ARG_CONTENT" "$ARG_NOTEBOOK" "$ARG_TAGS" "$ARG_EDIT")
    
    debug_log "create_note returned: $note_id"
    
    if [ $? -ne 0 ] || [ -z "$note_id" ]; then
        log_error "Failed to create note"
        exit 1
    fi
    
    # Sync if requested
    if [ "$ARG_SYNC" = true ]; then
        log_info "Syncing Joplin..."
        joplin_noninteractive sync > /dev/null 2>&1 && log_success "Sync completed" || log_warning "Sync had issues"
    fi
    
    # Output result
    if [ "$ARG_QUIET" = false ]; then
        echo -e "${GREEN}✅ Note created successfully!${NC}"
        echo -e "${BLUE}Title:${NC} $ARG_TITLE"
        echo -e "${BLUE}Notebook:${NC} $ARG_NOTEBOOK"
        echo -e "${BLUE}Tags:${NC} $ARG_TAGS"
        echo -e "${BLUE}Note ID:${NC} $note_id"
        
        if [ "$ARG_EDIT" = false ]; then
            echo -e "${BLUE}Preview:${NC}"
            echo "$ARG_CONTENT" | head -5 | sed 's/^/  /'
            if [ $(echo "$ARG_CONTENT" | wc -l) -gt 5 ]; then
                echo "  ... (truncated)"
            fi
        fi
    else
        echo "$note_id"
    fi
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi