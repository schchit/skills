#!/bin/bash
cmd_list() { local filter="$*"
    if [ -z "$filter" ]; then ps aux --sort=-%cpu | head -30
    else ps aux | grep -i "$filter" | grep -v grep; fi
}
cmd_top() { local n="${1:-10}"; echo "=== Top $n by CPU ==="; ps aux --sort=-%cpu | head -$((n+1)); }
cmd_mem() { local n="${1:-10}"; echo "=== Top $n by Memory ==="; ps aux --sort=-%mem | head -$((n+1)); }
cmd_watch() { local pid="$1"; [ -z "$pid" ] && { echo "Usage: procmon watch <pid>"; return 1; }
    echo "Monitoring PID $pid (5 samples, 2s interval):"
    for i in 1 2 3 4 5; do
        local info=$(ps -o %cpu,%mem,rss,vsz -p "$pid" 2>/dev/null | tail -1)
        [ -z "$info" ] && { echo "Process $pid not found"; return 1; }
        echo "  $(date +%H:%M:%S) $info"
        [ "$i" -lt 5 ] && sleep 2
    done
}
cmd_tree() { pstree -p 2>/dev/null || ps axjf 2>/dev/null | head -40 || echo "pstree not available"; }
cmd_find() { local name="$1"; [ -z "$name" ] && { echo "Usage: procmon find <name>"; return 1; }
    echo "=== Processes matching '$name' ==="
    ps aux | grep -i "$name" | grep -v grep | grep -v "procmon find"
    echo ""; pgrep -c "$name" 2>/dev/null && echo " process(es) found" || true
}
cmd_signal() { local pid="$1" sig="${2:-TERM}"
    [ -z "$pid" ] && { echo "Usage: procmon signal <pid> <TERM|KILL|HUP|USR1|...>"; return 1; }
    kill -"$sig" "$pid" 2>/dev/null && echo "Sent $sig to PID $pid" || echo "Failed to signal PID $pid"
}
cmd_help() { echo "ProcMon - Process Monitor & Manager"; echo "Commands: list [filter] | top [n] | mem [n] | watch <pid> | tree | find <name> | signal <pid> <sig> | help"; }
cmd_info() { echo "ProcMon v1.0.0 | Powered by BytesAgain"; }
case "$1" in list) shift; cmd_list "$@";; top) shift; cmd_top "$@";; mem) shift; cmd_mem "$@";; watch) shift; cmd_watch "$@";; tree) cmd_tree;; find) shift; cmd_find "$@";; signal) shift; cmd_signal "$@";; info) cmd_info;; help|"") cmd_help;; *) cmd_help; exit 1;; esac
