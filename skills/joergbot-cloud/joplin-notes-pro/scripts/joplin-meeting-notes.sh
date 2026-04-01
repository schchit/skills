#!/bin/bash
# Joplin Meeting Notes Script
# Create structured meeting notes with action items and follow-ups

set -e

# Source the check script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/joplin-check.sh"

# Configuration
MEETING_NOTEBOOK="${JOPLIN_MEETING_NOTEBOOK:-Meetings}"
MEETING_TAGS="${JOPLIN_MEETING_TAGS:-meeting,work}"
DATE_FORMAT="${JOPLIN_DATE_FORMAT:-%Y-%m-%d}"
TIME_FORMAT="${JOPLIN_TIME_FORMAT:-%H:%M}"
EDITOR="${EDITOR:-vi}"

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
Joplin Meeting Notes Script
Create structured meeting notes with action items, decisions, and follow-ups.

Usage: $0 [OPTIONS] "Meeting Title"

Options:
  -d, --date DATE        Meeting date (default: today)
  -t, --time TIME        Meeting time (format: HH:MM)
  -l, --location LOC     Meeting location
  -a, --attendees LIST   Comma-separated list of attendees
  -f, --facilitator NAME Meeting facilitator
  -n, --notebook NAME    Meeting notebook (default: Meetings)
  --tags TAG1,TAG2       Additional tags (default: meeting,work)
  -g, --agenda ITEMS     Comma-separated agenda items
  -o, --objectives ITEMS Comma-separated objectives
  -e, --edit             Open in editor after creation
  -s, --sync             Sync after creating notes
  -T, --template NAME    Template: standard, quick, retrospective, client
  -h, --help             Show this help message

Templates:
  standard       Standard meeting with agenda, notes, action items
  quick          Quick meeting (15-min standup style)
  retrospective  Retrospective meeting (what went well, improvements)
  client         Client meeting (objectives, deliverables, next steps)

Examples:
  $0 "Team Standup" -t "09:30" -a "Alice,Bob,Charlie"
  $0 "Project Review" -g "Status,Blockers,Next Steps" -o "Align on timeline"
  $0 "Client Call" -T client -f "Jörg" -a "Client Name"
  $0 "Retrospective" -T retrospective --tags "retro,team"

Environment Variables:
  JOPLIN_MEETING_NOTEBOOK  Default meeting notebook
  JOPLIN_MEETING_TAGS      Default meeting tags
  JOPLIN_DATE_FORMAT       Date format
  JOPLIN_TIME_FORMAT       Time format
  EDITOR                   Editor to use

EOF
}

# Get template content
get_meeting_template() {
    local template_name="$1"
    local title="$2"
    local date_str="$3"
    local time_str="$4"
    local location="$5"
    local attendees="$6"
    local facilitator="$7"
    local agenda="$8"
    local objectives="$9"
    
    # Format attendees list
    local attendees_list=""
    if [ -n "$attendees" ]; then
        IFS=',' read -ra attendee_array <<< "$attendees"
        for attendee in "${attendee_array[@]}"; do
            attendees_list="${attendees_list}- $(echo "$attendee" | xargs)\n"
        done
    fi
    
    # Format agenda items
    local agenda_list=""
    if [ -n "$agenda" ]; then
        IFS=',' read -ra agenda_array <<< "$agenda"
        local counter=1
        for item in "${agenda_array[@]}"; do
            agenda_list="${agenda_list}$counter. $(echo "$item" | xargs)\n"
            counter=$((counter + 1))
        done
    fi
    
    # Format objectives
    local objectives_list=""
    if [ -n "$objectives" ]; then
        IFS=',' read -ra obj_array <<< "$objectives"
        for obj in "${obj_array[@]}"; do
            objectives_list="${objectives_list}- $(echo "$obj" | xargs)\n"
        done
    fi
    
    case "$template_name" in
        standard)
            cat << EOF
# $title

## 📅 Meeting Details
**Date:** $date_str
**Time:** $time_str
**Location:** ${location:-Not specified}
**Attendees:**
${attendees_list:-- Not specified}
**Facilitator:** ${facilitator:-Not specified}

## 🎯 Objectives
${objectives_list:-- Define meeting objectives}

## 📋 Agenda
${agenda_list:-1. 
2. 
3. }

## 📝 Discussion Notes
**Topic 1:**
- 

**Topic 2:**
- 

**Topic 3:**
- 

## ✅ Action Items
| Who | What | By When | Status |
|-----|------|---------|--------|
|     |      |         |        |
|     |      |         |        |
|     |      |         |        |

## 🎯 Decisions Made
1. 
2. 

## 🔄 Next Steps
- 

## 📎 Attachments & References
- 

---
*Meeting Notes - $date_str $time_str*
EOF
            ;;
        
        quick)
            cat << EOF
# $title

## ⚡ Quick Meeting - $date_str $time_str

**Attendees:** ${attendees:-Quick team sync}
**Duration:** 15 minutes

## 🚀 What's Up?
**Updates from team:**
- 

**Blockers:**
- 

**Quick Wins:**
- 

## 🎯 Today's Focus
- 

## ⚠️ Urgent Items
- 

## 🤝 Help Needed
- 

---
*Quick Meeting - $date_str*
EOF
            ;;
        
        retrospective)
            cat << EOF
# $title

## 🔄 Retrospective - $date_str

**Period:** [Sprint/Week/Month]
**Attendees:**
${attendees_list:-Full team}

## 🌟 What Went Well
- 

## 📈 What Could Be Improved
- 

## 💡 Ideas & Suggestions
- 

## 🎯 Action Items for Next Period
| Action | Owner | Timeline |
|--------|-------|----------|
|        |       |          |
|        |       |          |

## 🙏 Appreciations
- 

---
*Retrospective - $date_str*
EOF
            ;;
        
        client)
            cat << EOF
# $title

## 🤝 Client Meeting - $date_str

**Client:** ${attendees:-Client name}
**Company:** 
**Attendees (Our side):** ${facilitator:-Our team}
**Meeting Type:** [Kickoff, Review, Check-in, Final]

## 🎯 Meeting Objectives
${objectives_list:-1. 
2. 
3. }

## 📋 Agenda
${agenda_list:-1. Introductions & Recap
2. Project Updates
3. Discussion Points
4. Next Steps
5. Q&A}

## 💼 Discussion Points
**Client Feedback:**
- 

**Our Updates:**
- 

**Key Decisions:**
- 

## 📦 Deliverables & Timeline
| Deliverable | Owner | Due Date | Status |
|-------------|-------|----------|--------|
|             |       |          |        |
|             |       |          |        |

## 💰 Financial Discussion
- 

## 📅 Next Steps & Follow-ups
- 

## 📞 Contact Information
- 

---
*Client Meeting - $date_str*
EOF
            ;;
        
        *)
            # Default template
            cat << EOF
# $title

## Meeting Details
Date: $date_str
Time: $time_str
Location: ${location:-}
Attendees: ${attendees:-}
Facilitator: ${facilitator:-}

## Agenda
${agenda_list:-}

## Notes
- 

## Action Items
- 

---
$date_str
EOF
            ;;
    esac
}

# Parse arguments
parse_args() {
    local meeting_title=""
    local meeting_date=""
    local meeting_time=""
    local location=""
    local attendees=""
    local facilitator=""
    local notebook=""
    local tags=""
    local agenda=""
    local objectives=""
    local template="standard"
    local do_edit=false
    local do_sync=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--date)
                meeting_date="$2"
                shift 2
                ;;
            -t|--time)
                meeting_time="$2"
                shift 2
                ;;
            -l|--location)
                location="$2"
                shift 2
                ;;
            -a|--attendees)
                attendees="$2"
                shift 2
                ;;
            -f|--facilitator)
                facilitator="$2"
                shift 2
                ;;
            -n|--notebook)
                notebook="$2"
                shift 2
                ;;
            --tags)
                tags="$2"
                shift 2
                ;;
            -g|--agenda)
                agenda="$2"
                shift 2
                ;;
            -o|--objectives)
                objectives="$2"
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
            -T|--template)
                template="$2"
                shift 2
                ;;
            --)
                shift
                meeting_title="$*"
                break
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                # First non-option argument is meeting title
                if [ -z "$meeting_title" ]; then
                    meeting_title="$1"
                else
                    log_error "Unexpected argument: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Validate required arguments
    if [ -z "$meeting_title" ]; then
        log_error "Meeting title is required"
        show_help
        exit 1
    fi
    
    # Set defaults
    meeting_date="${meeting_date:-$(date +"$DATE_FORMAT")}"
    meeting_time="${meeting_time:-$(date +"$TIME_FORMAT")}"
    notebook="${notebook:-$MEETING_NOTEBOOK}"
    
    # Build tags
    if [ -n "$tags" ]; then
        tags="$MEETING_TAGS,$tags"
    else
        tags="$MEETING_TAGS"
    fi
    
    # Add template-specific tag
    tags="$tags,$template"
    
    # Return values
    ARG_TITLE="$meeting_title"
    ARG_DATE="$meeting_date"
    ARG_TIME="$meeting_time"
    ARG_LOCATION="$location"
    ARG_ATTENDEES="$attendees"
    ARG_FACILITATOR="$facilitator"
    ARG_NOTEBOOK="$notebook"
    ARG_TAGS="$tags"
    ARG_AGENDA="$agenda"
    ARG_OBJECTIVES="$objectives"
    ARG_TEMPLATE="$template"
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
    
    # Display meeting info
    echo -e "${PURPLE}📋 Creating Meeting Notes${NC}"
    echo -e "${BLUE}Title:${NC} $ARG_TITLE"
    echo -e "${BLUE}Date/Time:${NC} $ARG_DATE $ARG_TIME"
    echo -e "${BLUE}Location:${NC} ${ARG_LOCATION:-Not specified}"
    echo -e "${BLUE}Attendees:${NC} ${ARG_ATTENDEES:-Not specified}"
    echo -e "${BLUE}Facilitator:${NC} ${ARG_FACILITATOR:-Not specified}"
    echo -e "${BLUE}Notebook:${NC} $ARG_NOTEBOOK"
    echo -e "${BLUE}Tags:${NC} $ARG_TAGS"
    echo -e "${BLUE}Template:${NC} $ARG_TEMPLATE"
    echo ""
    
    # Get template content
    local meeting_content=$(get_meeting_template \
        "$ARG_TEMPLATE" \
        "$ARG_TITLE" \
        "$ARG_DATE" \
        "$ARG_TIME" \
        "$ARG_LOCATION" \
        "$ARG_ATTENDEES" \
        "$ARG_FACILITATOR" \
        "$ARG_AGENDA" \
        "$ARG_OBJECTIVES")
    
    # Create the meeting notes using quick-note script
    log_info "Creating meeting notes..."
    
    # Use quick-note script to create the entry
    note_id=$("$SCRIPT_DIR/joplin-quick-note.sh" \
        --quiet \
        --title "$ARG_TITLE" \
        --notebook "$ARG_NOTEBOOK" \
        --tags "$ARG_TAGS" \
        $( [ "$ARG_EDIT" = true ] && echo "--edit" ) \
        $( [ "$ARG_SYNC" = true ] && echo "--sync" ) \
        "$meeting_content")
    
    if [ $? -ne 0 ] || [ -z "$note_id" ]; then
        log_error "Failed to create meeting notes"
        exit 1
    fi
    
    # Success message
    echo -e "${GREEN}✅ Meeting notes created successfully!${NC}"
    echo -e "${BLUE}Note ID:${NC} $note_id"
    echo ""
    
    # Show preview if not editing
    if [ "$ARG_EDIT" = false ]; then
        echo -e "${BLUE}Preview:${NC}"
        echo "$meeting_content" | head -15 | sed 's/^/  /'
        if [ $(echo "$meeting_content" | wc -l) -gt 15 ]; then
            echo "  ... (use --edit to see full content)"
        fi
    fi
    
    # Additional tips
    echo ""
    echo -e "${PURPLE}💡 Meeting Management Tips:${NC}"
    echo "  • View notes: joplin cat $note_id"
    echo "  • Edit notes: joplin edit $note_id"
    echo "  • Add action items: Edit the 'Action Items' section"
    echo "  • Follow up: Set calendar reminder for action item due dates"
    echo "  • Share: Export as Markdown to share with attendees"
    
    # Sync reminder
    if [ "$ARG_SYNC" = false ]; then
        echo "  • Sync to cloud: joplin sync"
    fi
    
    # Template-specific tips
    case "$ARG_TEMPLATE" in
        retrospective)
            echo ""
            echo -e "${YELLOW}📊 Retrospective Best Practices:${NC}"
            echo "  • Review previous retrospective action items"
            echo "  • Focus on processes, not people"
            echo "  • Assign owners to all action items"
            echo "  • Schedule follow-up for action item review"
            ;;
        client)
            echo ""
            echo -e "${YELLOW}🤝 Client Meeting Best Practices:${NC}"
            echo "  • Send agenda to client before meeting"
            echo "  • Share notes with client after meeting"
            echo "  • Follow up on action items within 24 hours"
            echo "  • Set clear expectations for next steps"
            ;;
    esac
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi