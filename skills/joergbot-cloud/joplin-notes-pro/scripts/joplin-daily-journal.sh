#!/bin/bash
# Joplin Daily Journal Script
# Create daily journal entries with consistent formatting

set -e

# Source the check script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/joplin-check.sh"

# Configuration
JOURNAL_NOTEBOOK="${JOPLIN_JOURNAL_NOTEBOOK:-Journal}"
JOURNAL_TAGS="${JOPLIN_JOURNAL_TAGS:-journal,daily}"
DATE_FORMAT="${JOPLIN_DATE_FORMAT:-%Y-%m-%d}"
EDITOR="${EDITOR:-vi}"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Help function
show_help() {
    cat << EOF
Joplin Daily Journal Script
Create consistent daily journal entries with templates.

Usage: $0 [OPTIONS]

Options:
  -d, --date DATE        Use specific date (format: YYYY-MM-DD)
  -t, --title TITLE      Custom title (default: "Journal YYYY-MM-DD")
  -n, --notebook NAME    Journal notebook (default: Journal)
  --tags TAG1,TAG2       Additional tags (default: journal,daily)
  -e, --edit             Open in editor after creation
  -t, --template NAME    Use template (daily, weekly, meeting, project)
  --no-template          Don't use any template
  -s, --sync             Sync after creating entry
  -h, --help             Show this help message

Environment Variables:
  JOPLIN_JOURNAL_NOTEBOOK  Journal notebook (default: Journal)
  JOPLIN_JOURNAL_TAGS      Default tags (default: journal,daily)
  JOPLIN_DATE_FORMAT       Date format (default: %Y-%m-%d)
  EDITOR                   Editor to use

Templates:
  daily     Daily journal with sections
  weekly    Weekly review template  
  meeting   Meeting notes template
  project   Project update template

Examples:
  $0                        # Create today's journal
  $0 -d 2026-03-28          # Create journal for specific date
  $0 -t "Weekly Review" -t weekly  # Weekly review
  $0 --edit                 # Create and open in editor
  $0 --no-template          # Create empty journal entry

EOF
}

# Get template content
get_template() {
    local template_name="$1"
    local date_str="$2"
    local weekday="$3"
    
    case "$template_name" in
        daily)
            cat << EOF
# Journal $date_str ($weekday)

## 🎯 Today's Focus
- 

## 📝 Notes & Ideas
- 

## ✅ Completed Tasks
- 

## 🔄 Carry Forward
- 

## 🌟 Highlights
- 

## 📚 Learning
- 

## 💭 Reflection
- 

---
*Created with Joplin Daily Journal Script*
EOF
            ;;
        weekly)
            cat << EOF
# Weekly Review - Week of $date_str

## 📊 Week in Review
**Accomplishments:**
- 

**Challenges:**
- 

**Learnings:**
- 

## 🎯 Goals for Next Week
1. 
2. 
3. 

## 📈 Metrics & Progress
- 

## 🔄 Process Improvements
- 

## 🙏 Gratitude
- 

---
*Weekly Review - $date_str*
EOF
            ;;
        meeting)
            cat << EOF
# Meeting Notes - $date_str

## 📅 Meeting Details
**Date:** $date_str
**Time:** 
**Location:** 
**Attendees:** 
**Facilitator:** 

## 🎯 Agenda & Objectives
1. 
2. 
3. 

## 📝 Discussion Notes
**Topic 1:**
- 

**Topic 2:**
- 

**Topic 3:**
- 

## ✅ Action Items
| Who | What | By When |
|-----|------|---------|
|     |      |         |
|     |      |         |

## 🎯 Decisions Made
1. 
2. 

## 🔄 Next Steps
- 

---
*Meeting Notes - $date_str*
EOF
            ;;
        project)
            cat << EOF
# Project Update - $date_str

## 📋 Project Status
**Project:** 
**Date:** $date_str
**Status:** ⚪ Not Started / 🟡 In Progress / 🟢 Completed / 🔴 Blocked

## 🎯 This Week's Objectives
1. 
2. 
3. 

## ✅ Completed This Week
- 

## 🚧 Current Work
- 

## 🚨 Blockers & Issues
- 

## 📅 Next Week's Plan
- 

## 📊 Metrics & KPIs
- 

## 💡 Insights & Learnings
- 

---
*Project Update - $date_str*
EOF
            ;;
        *)
            # Empty template
            echo "# Journal $date_str"
            echo ""
            ;;
    esac
}

# Get weekday name in German
get_german_weekday() {
    local date_str="$1"
    local weekday_num=$(date -d "$date_str" +%u 2>/dev/null || date -j -f "%Y-%m-%d" "$date_str" +%u 2>/dev/null)
    
    case $weekday_num in
        1) echo "Montag" ;;
        2) echo "Dienstag" ;;
        3) echo "Mittwoch" ;;
        4) echo "Donnerstag" ;;
        5) echo "Freitag" ;;
        6) echo "Samstag" ;;
        7) echo "Sonntag" ;;
        *) echo "" ;;
    esac
}

# Parse arguments
parse_args() {
    local custom_date=""
    local custom_title=""
    local custom_notebook=""
    local custom_tags=""
    local template="daily"
    local do_edit=false
    local do_sync=false
    local no_template=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--date)
                custom_date="$2"
                shift 2
                ;;
            -t|--title)
                custom_title="$2"
                shift 2
                ;;
            -n|--notebook)
                custom_notebook="$2"
                shift 2
                ;;
            --tags)
                custom_tags="$2"
                shift 2
                ;;
            -e|--edit)
                do_edit=true
                shift
                ;;
            --template)
                template="$2"
                shift 2
                ;;
            --no-template)
                no_template=true
                shift
                ;;
            -s|--sync)
                do_sync=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                # Assume it's a template name if no option
                template="$1"
                shift
                ;;
        esac
    done
    
    # Set date
    if [ -n "$custom_date" ]; then
        journal_date="$custom_date"
    else
        journal_date=$(date +"$DATE_FORMAT")
    fi
    
    # Validate date format
    if ! date -d "$journal_date" >/dev/null 2>&1 && ! date -j -f "%Y-%m-%d" "$journal_date" >/dev/null 2>&1; then
        log_error "Invalid date format: $journal_date. Use YYYY-MM-DD."
        exit 1
    fi
    
    # Get weekday
    weekday=$(get_german_weekday "$journal_date")
    
    # Set title
    if [ -n "$custom_title" ]; then
        journal_title="$custom_title"
    else
        journal_title="Journal $journal_date"
        if [ -n "$weekday" ]; then
            journal_title="$journal_title ($weekday)"
        fi
    fi
    
    # Set notebook
    journal_notebook="${custom_notebook:-$JOURNAL_NOTEBOOK}"
    
    # Set tags
    if [ -n "$custom_tags" ]; then
        journal_tags="$JOURNAL_TAGS,$custom_tags"
    else
        journal_tags="$JOURNAL_TAGS"
    fi
    
    # Set template
    if [ "$no_template" = true ]; then
        journal_template="none"
    else
        journal_template="$template"
    fi
    
    # Return values
    ARG_DATE="$journal_date"
    ARG_TITLE="$journal_title"
    ARG_NOTEBOOK="$journal_notebook"
    ARG_TAGS="$journal_tags"
    ARG_TEMPLATE="$journal_template"
    ARG_WEEKDAY="$weekday"
    ARG_EDIT="$do_edit"
    ARG_SYNC="$do_sync"
}

# Main function
main() {
    parse_args "$@"
    
    # Check Joplin health
    if ! check_joplin_health > /dev/null 2>&1; then
        log_error "Joplin health check failed. Please fix Joplin installation."
        check_joplin_health
        exit 1
    fi
    
    # Get template content
    if [ "$ARG_TEMPLATE" = "none" ]; then
        journal_content="# $ARG_TITLE"
    else
        journal_content=$(get_template "$ARG_TEMPLATE" "$ARG_DATE" "$ARG_WEEKDAY")
    fi
    
    # Display information
    echo -e "${PURPLE}📔 Creating Daily Journal Entry${NC}"
    echo -e "${BLUE}Date:${NC} $ARG_DATE ($ARG_WEEKDAY)"
    echo -e "${BLUE}Title:${NC} $ARG_TITLE"
    echo -e "${BLUE}Notebook:${NC} $ARG_NOTEBOOK"
    echo -e "${BLUE}Tags:${NC} $ARG_TAGS"
    echo -e "${BLUE}Template:${NC} $ARG_TEMPLATE"
    echo ""
    
    # Create the journal entry using quick-note script
    log_info "Creating journal entry..."
    
    # Use quick-note script to create the entry
    note_id=$("$SCRIPT_DIR/joplin-quick-note.sh" \
        --quiet \
        --title "$ARG_TITLE" \
        --notebook "$ARG_NOTEBOOK" \
        --tags "$ARG_TAGS" \
        $( [ "$ARG_EDIT" = true ] && echo "--edit" ) \
        $( [ "$ARG_SYNC" = true ] && echo "--sync" ) \
        "$journal_content")
    
    if [ $? -ne 0 ] || [ -z "$note_id" ]; then
        log_error "Failed to create journal entry"
        exit 1
    fi
    
    # Success message
    echo -e "${GREEN}✅ Journal entry created successfully!${NC}"
    echo -e "${BLUE}Note ID:${NC} $note_id"
    echo ""
    
    # Show preview if not editing
    if [ "$ARG_EDIT" = false ]; then
        echo -e "${BLUE}Preview:${NC}"
        echo "$journal_content" | head -10 | sed 's/^/  /'
        if [ $(echo "$journal_content" | wc -l) -gt 10 ]; then
            echo "  ... (use --edit to see full content)"
        fi
    fi
    
    # Additional tips
    echo ""
    echo -e "${PURPLE}💡 Tips:${NC}"
    echo "  • View note: joplin cat $note_id"
    echo "  • Edit note: joplin edit $note_id"
    echo "  • List all journals: joplin ls '$ARG_NOTEBOOK'"
    
    # Sync reminder
    if [ "$ARG_SYNC" = false ]; then
        echo "  • Sync to cloud: joplin sync"
    fi
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi