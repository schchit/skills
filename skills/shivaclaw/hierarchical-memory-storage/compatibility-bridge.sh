#!/usr/bin/env bash
# Compatibility bridge for hierarchical-memory with popular self-improvement skills
# Ensures graceful coexistence and optional migration paths

set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
MEMORY_ROOT="$WORKSPACE/memory"

# Detect which self-improvement skills are installed
detect_skills() {
    local skills=()
    
    # Check for pskoett/self-improving-agent (.learnings/)
    if [[ -d "$WORKSPACE/.learnings" ]]; then
        skills+=("pskoett")
    fi
    
    # Check for halthelobster/proactive-agent (SESSION-STATE.md, working-buffer.md)
    if [[ -f "$WORKSPACE/SESSION-STATE.md" ]] || [[ -f "$WORKSPACE/memory/working-buffer.md" ]]; then
        skills+=("proactive")
    fi
    
    # Check for ivangdavila/self-improving (~/self-improving/)
    if [[ -d "$HOME/self-improving" ]]; then
        skills+=("ivangdavila")
    fi
    
    echo "${skills[@]}"
}

# Create compatibility symlinks or aliases
setup_bridges() {
    local skills=("$@")
    
    for skill in "${skills[@]}"; do
        case "$skill" in
            pskoett)
                echo "🔗 Bridging pskoett/self-improving-agent (.learnings/)"
                # Symlink .learnings/ content into memory/lessons/
                if [[ ! -L "$MEMORY_ROOT/lessons/.learnings" ]]; then
                    ln -sf "$WORKSPACE/.learnings" "$MEMORY_ROOT/lessons/.learnings" 2>/dev/null || true
                fi
                ;;
            proactive)
                echo "🔗 Bridging halthelobster/proactive-agent (SESSION-STATE, working-buffer)"
                # Symlink SESSION-STATE.md and working-buffer.md into memory/
                if [[ -f "$WORKSPACE/SESSION-STATE.md" ]] && [[ ! -L "$MEMORY_ROOT/SESSION-STATE.md" ]]; then
                    ln -sf "$WORKSPACE/SESSION-STATE.md" "$MEMORY_ROOT/SESSION-STATE.md" 2>/dev/null || true
                fi
                if [[ -f "$WORKSPACE/memory/working-buffer.md" ]] && [[ ! -f "$MEMORY_ROOT/working-buffer.md" ]]; then
                    # Already in memory/, no action needed
                    :
                fi
                ;;
            ivangdavila)
                echo "🔗 Bridging ivangdavila/self-improving (~/self-improving/)"
                # Symlink ~/self-improving/ into memory/
                if [[ ! -L "$MEMORY_ROOT/.self-improving" ]]; then
                    ln -sf "$HOME/self-improving" "$MEMORY_ROOT/.self-improving" 2>/dev/null || true
                fi
                ;;
        esac
    done
}

# Read from legacy skills during consolidation
read_legacy_learnings() {
    echo "## Legacy Skill Learnings"
    echo ""
    
    # pskoett: Read .learnings/LEARNINGS.md
    if [[ -f "$WORKSPACE/.learnings/LEARNINGS.md" ]]; then
        echo "### From pskoett/self-improving-agent (.learnings/LEARNINGS.md)"
        tail -n 20 "$WORKSPACE/.learnings/LEARNINGS.md"
        echo ""
    fi
    
    # proactive: Read SESSION-STATE.md
    if [[ -f "$WORKSPACE/SESSION-STATE.md" ]]; then
        echo "### From halthelobster/proactive-agent (SESSION-STATE.md)"
        tail -n 10 "$WORKSPACE/SESSION-STATE.md"
        echo ""
    fi
    
    # ivangdavila: Read ~/self-improving/corrections.md
    if [[ -f "$HOME/self-improving/corrections.md" ]]; then
        echo "### From ivangdavila/self-improving (corrections.md)"
        tail -n 15 "$HOME/self-improving/corrections.md"
        echo ""
    fi
}

# Optional: Migrate legacy learnings into hierarchical structure
migrate_legacy() {
    echo "🔄 Migrating legacy learnings into hierarchical-memory structure..."
    
    # pskoett → memory/lessons/
    if [[ -d "$WORKSPACE/.learnings" ]]; then
        echo "  - Copying .learnings/LEARNINGS.md → memory/lessons/pskoett-learnings.md"
        cp "$WORKSPACE/.learnings/LEARNINGS.md" "$MEMORY_ROOT/lessons/pskoett-learnings.md" 2>/dev/null || true
        
        echo "  - Copying .learnings/ERRORS.md → memory/lessons/pskoett-errors.md"
        cp "$WORKSPACE/.learnings/ERRORS.md" "$MEMORY_ROOT/lessons/pskoett-errors.md" 2>/dev/null || true
    fi
    
    # proactive → memory/
    if [[ -f "$WORKSPACE/SESSION-STATE.md" ]]; then
        echo "  - Copying SESSION-STATE.md → memory/session-state-proactive.md"
        cp "$WORKSPACE/SESSION-STATE.md" "$MEMORY_ROOT/session-state-proactive.md" 2>/dev/null || true
    fi
    
    # ivangdavila → memory/lessons/
    if [[ -f "$HOME/self-improving/memory.md" ]]; then
        echo "  - Copying ~/self-improving/memory.md → memory/lessons/ivangdavila-memory.md"
        cp "$HOME/self-improving/memory.md" "$MEMORY_ROOT/lessons/ivangdavila-memory.md" 2>/dev/null || true
        
        echo "  - Copying ~/self-improving/corrections.md → memory/lessons/ivangdavila-corrections.md"
        cp "$HOME/self-improving/corrections.md" "$MEMORY_ROOT/lessons/ivangdavila-corrections.md" 2>/dev/null || true
    fi
    
    echo "✅ Migration complete. Review memory/lessons/ for imported content."
}

# Main CLI
case "${1:-detect}" in
    detect)
        echo "🔍 Detecting installed self-improvement skills..."
        skills=($(detect_skills))
        if [[ ${#skills[@]} -eq 0 ]]; then
            echo "No legacy skills detected."
        else
            echo "Found: ${skills[*]}"
        fi
        ;;
    bridge)
        echo "🔗 Setting up compatibility bridges..."
        skills=($(detect_skills))
        setup_bridges "${skills[@]}"
        echo "✅ Bridges configured."
        ;;
    read)
        read_legacy_learnings
        ;;
    migrate)
        migrate_legacy
        ;;
    *)
        echo "Usage: $0 {detect|bridge|read|migrate}"
        echo ""
        echo "Commands:"
        echo "  detect   - Detect which self-improvement skills are installed"
        echo "  bridge   - Create symlinks for graceful coexistence"
        echo "  read     - Display recent learnings from legacy skills"
        echo "  migrate  - Copy legacy learnings into hierarchical-memory structure"
        exit 1
        ;;
esac
