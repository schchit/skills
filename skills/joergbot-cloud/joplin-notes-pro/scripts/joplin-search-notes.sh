#!/bin/bash
# Joplin Search Notes Script
# Advanced note search with filters and multiple output formats

set -e

# Source the check script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/joplin-check.sh"

# Configuration
SEARCH_LIMIT="${JOPLIN_SEARCH_LIMIT:-50}"
OUTPUT_FORMAT="${JOPLIN_SEARCH_FORMAT:-table}"

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
Joplin Search Notes Script
Advanced note search with filters, sorting, and multiple output formats.

Usage: $0 [OPTIONS] "search query"

Options:
  -l, --limit N          Maximum results (default: 50)
  -n, --notebook NAME    Filter by notebook
  -t, --tag TAG          Filter by tag
  -s, --sort FIELD       Sort by: title, updated, created (default: updated)
  -r, --reverse          Reverse sort order
  -f, --format FORMAT    Output format: table, json, csv, list, markdown
  -c, --content          Include note content in output
  -d, --details          Show detailed information
  -o, --output FILE      Write results to file
  -q, --quiet            Quiet mode (minimal output)
  -h, --help             Show this help message

Search Operators:
  "exact phrase"         Exact phrase match
  word1 word2           AND search (both words)
  word1 OR word2        OR search (either word)
  -exclude              Exclude word
  tag:work              Search by tag
  notebook:Projects     Search in notebook
  is:todo               Search to-dos
  created:2026-03       Created in March 2026
  updated:2026-03-28    Updated on specific date

Examples:
  $0 "project meeting"                    # Basic search
  $0 "important OR urgent" -t work        # Search with tag filter
  $0 "notebook:Journal" -s created -r     # Sort by creation date (newest first)
  $0 "tag:todo is:todo" -f json -o output.json  # JSON output
  $0 "daily" --content --limit 10         # Include note content

Environment Variables:
  JOPLIN_SEARCH_LIMIT    Default result limit
  JOPLIN_SEARCH_FORMAT   Default output format

EOF
}

# Parse command line arguments
parse_args() {
    local search_query=""
    local limit="$SEARCH_LIMIT"
    local notebook=""
    local tag=""
    local sort_field="updated_time"
    local reverse=false
    local format="$OUTPUT_FORMAT"
    local include_content=false
    local show_details=false
    local output_file=""
    local quiet=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -l|--limit)
                limit="$2"
                shift 2
                ;;
            -n|--notebook)
                notebook="$2"
                shift 2
                ;;
            -t|--tag)
                tag="$2"
                shift 2
                ;;
            -s|--sort)
                case "$2" in
                    title) sort_field="title" ;;
                    updated|updated_time) sort_field="updated_time" ;;
                    created|created_time) sort_field="created_time" ;;
                    *) log_error "Invalid sort field: $2. Use: title, updated, created"
                       exit 1 ;;
                esac
                shift 2
                ;;
            -r|--reverse)
                reverse=true
                shift
                ;;
            -f|--format)
                format="$2"
                shift 2
                ;;
            -c|--content)
                include_content=true
                shift
                ;;
            -d|--details)
                show_details=true
                shift
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            -q|--quiet)
                quiet=true
                shift
                ;;
            --)
                shift
                search_query="$*"
                break
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                # Accumulate search query
                if [ -z "$search_query" ]; then
                    search_query="$1"
                else
                    search_query="$search_query $1"
                fi
                shift
                ;;
        esac
    done
    
    # If search query not provided as arguments, check stdin
    if [ -z "$search_query" ] && ! tty -s; then
        search_query=$(cat -)
    fi
    
    # Validate required arguments
    if [ -z "$search_query" ]; then
        if [ "$quiet" = false ]; then
            log_warning "No search query provided. Showing all notes (limit: $limit)"
            search_query="*"
        else
            log_error "Search query is required in quiet mode"
            exit 1
        fi
    fi
    
    # Build search parameters
    local search_params=""
    
    # Add notebook filter
    if [ -n "$notebook" ]; then
        search_params="$search_params notebook:\"$notebook\" "
    fi
    
    # Add tag filter
    if [ -n "$tag" ]; then
        search_params="$search_params tag:\"$tag\" "
    fi
    
    # Final search query
    search_query="$search_params$search_query"
    
    # Return values
    ARG_QUERY="$search_query"
    ARG_LIMIT="$limit"
    ARG_SORT="$sort_field"
    ARG_REVERSE="$reverse"
    ARG_FORMAT="$format"
    ARG_CONTENT="$include_content"
    ARG_DETAILS="$show_details"
    ARG_OUTPUT="$output_file"
    ARG_QUIET="$quiet"
}

# Search notes using Joplin CLI
search_notes() {
    local query="$1"
    local limit="$2"
    local sort_field="$3"
    local reverse="$4"
    
    local search_cmd="joplin ls -l --limit $limit"
    
    # Add sort if specified
    if [ "$sort_field" != "updated_time" ]; then
        search_cmd="$search_cmd --order-by $sort_field"
    fi
    
    # Add reverse if specified
    if [ "$reverse" = true ]; then
        search_cmd="$search_cmd --reverse"
    fi
    
    # Execute search
    if [ "$query" = "*" ]; then
        # Show all notes
        eval "$search_cmd" 2>/dev/null || {
            log_error "Search failed"
            return 1
        }
    else
        # Search with query
        joplin ls -l --limit "$limit" "$query" 2>/dev/null || {
            log_error "Search failed for query: $query"
            return 1
        }
    fi
}

# Get note details
get_note_details() {
    local note_id="$1"
    
    # Get basic note info
    local note_info=$(joplin cat "$note_id" 2>/dev/null | head -20)
    local note_title=$(joplin ls -l | grep "^$note_id" | cut -c 34-)
    local note_updated=$(joplin ls -l | grep "^$note_id" | awk '{print $3, $4}')
    local note_created=$(joplin ls -l | grep "^$note_id" | awk '{print $5, $6}')
    
    # Get notebook
    local notebook=$(joplin ls | grep -B5 "$note_id" | grep -E "^[A-Z]" | head -1)
    
    # Get tags
    local tags=$(joplin tag list | grep "$note_id" | awk '{print $2}' | tr '\n' ',' | sed 's/,$//')
    
    echo "$note_id|$note_title|$notebook|$tags|$note_updated|$note_created|$note_info"
}

# Format output
format_output() {
    local data="$1"
    local format="$2"
    local include_content="$3"
    local show_details="$4"
    
    case "$format" in
        table)
            if [ "$show_details" = true ]; then
                echo -e "${BLUE}Search Results:${NC}"
                echo "=================================================================================="
                printf "%-36s | %-30s | %-15s | %s\n" "ID" "Title" "Notebook" "Updated"
                echo "=================================================================================="
                
                echo "$data" | while IFS='|' read -r id title notebook tags updated created content; do
                    # Truncate long titles
                    local short_title="${title:0:30}"
                    [ ${#title} -gt 30 ] && short_title="${short_title}..."
                    
                    local short_notebook="${notebook:0:15}"
                    [ ${#notebook} -gt 15 ] && short_notebook="${short_notebook}..."
                    
                    printf "%-36s | %-30s | %-15s | %s\n" "$id" "$short_title" "$short_notebook" "$updated"
                    
                    if [ "$include_content" = true ] && [ -n "$content" ]; then
                        echo "  Content: ${content:0:100}..."
                        echo "  -------------------------------------------------------------------------------"
                    fi
                done
            else
                # Simple table
                echo "$data" | awk -F'|' '{printf "%-36s | %-50s | %s\n", $1, substr($2,1,50), $5}'
            fi
            ;;
        
        json)
            echo "["
            local first=true
            echo "$data" | while IFS='|' read -r id title notebook tags updated created content; do
                if [ "$first" = true ]; then
                    first=false
                else
                    echo ","
                fi
                
                cat << EOF
  {
    "id": "$id",
    "title": "$(echo "$title" | sed 's/"/\\"/g')",
    "notebook": "$notebook",
    "tags": "$tags",
    "updated": "$updated",
    "created": "$created"$( [ "$include_content" = true ] && echo ",\n    \"content\": \"$(echo "$content" | sed 's/"/\\"/g' | tr '\n' ' ' | sed 's/  */ /g')\"" )
  }
EOF
            done
            echo "]"
            ;;
        
        csv)
            echo "id,title,notebook,tags,updated,created$( [ "$include_content" = true ] && echo ",content" )"
            echo "$data" | while IFS='|' read -r id title notebook tags updated created content; do
                echo "$id,\"$title\",\"$notebook\",\"$tags\",\"$updated\",\"$created\"$( [ "$include_content" = true ] && echo ",\"$(echo "$content" | sed 's/"/""/g' | tr '\n' ' ')\"" )"
            done
            ;;
        
        list)
            echo "$data" | while IFS='|' read -r id title notebook tags updated created content; do
                echo "- $title ($id)"
                echo "  Notebook: $notebook"
                echo "  Tags: $tags"
                echo "  Updated: $updated"
                [ "$include_content" = true ] && [ -n "$content" ] && echo "  Preview: ${content:0:100}..."
                echo ""
            done
            ;;
        
        markdown)
            echo "# Search Results"
            echo ""
            echo "**Query:** \`$ARG_QUERY\`"
            echo "**Found:** $(echo "$data" | wc -l) notes"
            echo ""
            echo "| ID | Title | Notebook | Tags | Updated |"
            echo "|----|-------|----------|------|---------|"
            
            echo "$data" | while IFS='|' read -r id title notebook tags updated created content; do
                local short_title="${title:0:50}"
                [ ${#title} -gt 50 ] && short_title="${short_title}..."
                
                local short_tags="${tags:0:20}"
                [ ${#tags} -gt 20 ] && short_tags="${short_tags}..."
                
                echo "| \`$id\` | $short_title | $notebook | $short_tags | $updated |"
                
                if [ "$include_content" = true ] && [ -n "$content" ]; then
                    echo ""
                    echo "**Content Preview:**"
                    echo "> ${content:0:200}..."
                    echo ""
                fi
            done
            ;;
        
        *)
            # Default: raw output
            echo "$data"
            ;;
    esac
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
    
    # Display search info
    if [ "$ARG_QUIET" = false ]; then
        echo -e "${PURPLE}🔍 Joplin Note Search${NC}"
        echo -e "${BLUE}Query:${NC} $ARG_QUERY"
        echo -e "${BLUE}Limit:${NC} $ARG_LIMIT results"
        echo -e "${BLUE}Sort:${NC} $ARG_SORT $( [ "$ARG_REVERSE" = true ] && echo "(reverse)" )"
        echo -e "${BLUE}Format:${NC} $ARG_FORMAT"
        echo ""
    fi
    
    # Perform search
    log_info "Searching notes..."
    local search_results=$(search_notes "$ARG_QUERY" "$ARG_LIMIT" "$ARG_SORT" "$ARG_REVERSE")
    
    if [ -z "$search_results" ]; then
        if [ "$ARG_QUIET" = false ]; then
            log_warning "No notes found matching your search criteria"
        fi
        exit 0
    fi
    
    # Process results
    local processed_results=""
    local result_count=0
    
    while IFS= read -r line; do
        if [ -n "$line" ] && [[ "$line" =~ ^[a-f0-9]{32} ]]; then
            local note_id=$(echo "$line" | awk '{print $1}')
            
            # Get note details
            local note_details=$(get_note_details "$note_id")
            processed_results="${processed_results}${note_details}\n"
            result_count=$((result_count + 1))
        fi
    done <<< "$search_results"
    
    # Remove trailing newline
    processed_results=$(echo -e "$processed_results" | sed '/^$/d')
    
    # Display result count
    if [ "$ARG_QUIET" = false ]; then
        echo -e "${GREEN}✅ Found $result_count notes${NC}"
        echo ""
    fi
    
    # Format output
    local formatted_output=$(format_output "$processed_results" "$ARG_FORMAT" "$ARG_CONTENT" "$ARG_DETAILS")
    
    # Output results
    if [ -n "$ARG_OUTPUT" ]; then
        echo "$formatted_output" > "$ARG_OUTPUT"
        if [ "$ARG_QUIET" = false ]; then
            log_success "Results saved to: $ARG_OUTPUT"
        fi
    else
        if [ "$ARG_QUIET" = true ]; then
            echo "$formatted_output"
        else
            echo "$formatted_output"
            
            # Show summary
            echo ""
            echo -e "${PURPLE}📊 Search Summary${NC}"
            echo -e "${BLUE}Total Results:${NC} $result_count"
            echo -e "${BLUE}Output Format:${NC} $ARG_FORMAT"
            
            if [ "$result_count" -eq "$ARG_LIMIT" ]; then
                echo -e "${YELLOW}⚠ Note: Results limited to $ARG_LIMIT. Use --limit to see more.${NC}"
            fi
        fi
    fi
    
    # Export tip
    if [ "$ARG_QUIET" = false ] && [ -z "$ARG_OUTPUT" ]; then
        echo ""
        echo -e "${BLUE}💡 Tips:${NC}"
        echo "  • Export to file: $0 [OPTIONS] -o results.json"
        echo "  • View note: joplin cat <note_id>"
        echo "  • Edit note: joplin edit <note_id>"
        echo "  • New search: $0 \"different query\""
    fi
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi