#!/usr/bin/env python3
"""
Proactive v1.0.10 - feedback_update.py
Changelog v1.0.10 (2026-03-30):
 + Sensor-Tags: CANDIDATE, GOAL, COMMITMENT, CONTEXT
 + SETUP-QUIET und SETUP-NOGO für Onboarding-Interview (Telegram)
 + Tags werden aus Nachricht extrahiert und in State gespeichert

Changelog v4.0 (2026-03-27):
 + Stress-Tracking: emotional_context in State
 + Stress-Level wird bei negativen/kurzen Antworten erhöht, bei positiven gesenkt

Changelog v3.0 (2026-03-26):
 + Positive Reaktion hebt temp_no_go (Dormant-Cooldown) sofort auf
 + Negative Reaktion setzt Topic direkt in temp_no_go (unabhängig vom Zähler)
"""

import json, sys, logging, argparse, re, time, os
from datetime import datetime, timezone, timedelta
import fcntl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "ping_history.json")
GRAPH_FILE = os.path.join(BASE_DIR, "interest_graph.json")
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
LOG_FILE = os.path.join(BASE_DIR, "logs", "proaktiv_cron.log")
LEARNING_RATE = 0.05
HARD_NEG_COOLDOWN_H = 24  # Stunden bei explizit negativer Reaktion

logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger()

def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default.copy()

def save_json(path, data):
    try:
        with open(path, "r+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.seek(0); f.truncate()
            json.dump(data, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
    except FileNotFoundError:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

def decode_sentiment(message: str, reply_delay_minutes: float) -> float:
    msg = message.lower().strip()
    if any(k in msg for k in ["ja", "cool", "geil", "super", "👍", "perfekt",
                               "nice", "danke", "genau", "stimmt", "🔥", "interessant"]):
        delta = +0.15
    elif any(k in msg for k in ["nö", "nee", "egal", "schon wieder", "nerve",
                                "hör auf", "stop", "🙄", "bitte nicht", "zu viel"]):
        delta = -0.25
    elif len(message) < 8:
        delta = -0.05
    elif len(message) > 50:
        delta = +0.10
    else:
        delta = +0.05

    if reply_delay_minutes > 120:
        delta *= 0.5
    elif reply_delay_minutes > 60:
        delta *= 0.75
    return round(delta * LEARNING_RATE, 4)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ping_id", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--delay_minutes", type=float, default=0)
    args = parser.parse_args()

    # ─── NEU v1.0.10: Session-ID Tracking ────────────────────────────────
    active_session = getattr(args, 'session_id', None)
    state_file_path = os.path.join(BASE_DIR, "proaktiv_state.json")
    fb_state = load_json(state_file_path, {})
    if active_session:
        fb_state["active_session_id"] = active_session
        save_json(state_file_path, fb_state)
    # ─────────────────────────────────────────────────────────────────────────

    # ─── NEU v4.2: Kuramas Sensoren auswerten ────────────────────────────────
    msg_text = args.message
    now_iso = datetime.now(timezone.utc).isoformat()
    state_file = os.path.join(BASE_DIR, "proaktiv_state.json")

    # 1. CANDIDATE (Neues Interesse)
    cand_match = re.search(r'\[CANDIDATE:\s*(.*?)\]', msg_text, re.IGNORECASE)
    if cand_match:
        candidate = cand_match.group(1).strip().lower()
        graph = load_json(GRAPH_FILE, {"interests": {}})
        candidates = graph.setdefault("candidate_topics", {})

        if candidate not in candidates:
            candidates[candidate] = {"mentions": 1, "positive_replies": 1, "last_seen": now_iso}
        else:
            candidates[candidate]["mentions"] += 1
            candidates[candidate]["positive_replies"] += 1
            candidates[candidate]["last_seen"] = now_iso

        save_json(GRAPH_FILE, graph)
        msg_text = re.sub(r'\[CANDIDATE:\s*.*?\]', '', msg_text, flags=re.IGNORECASE)

    # 2. GOAL (Ziel mit Deadline)
    goal_match = re.search(r'\[GOAL:\s*(.*?)\s*\|\s*DEADLINE:\s*(.*?)\]', msg_text, re.IGNORECASE)
    if goal_match:
        goal_desc = goal_match.group(1).strip()
        deadline = goal_match.group(2).strip()
        state = load_json(state_file, {})
        goals = state.setdefault("goals", {})

        goal_id = goal_desc.lower().replace(" ", "_")[:15]
        goals[goal_id] = {
            "description": goal_desc,
            "deadline": deadline,
            "status": "active"
        }
        save_json(state_file, state)
        msg_text = re.sub(r'\[GOAL:\s*.*?\]', '', msg_text, flags=re.IGNORECASE)

    # 3. COMMITMENT (Versprechen)
    comm_match = re.search(r'\[COMMITMENT:\s*(.*?)\s*\|\s*WHEN:\s*(.*?)\]', msg_text, re.IGNORECASE)
    if comm_match:
        comm_desc = comm_match.group(1).strip()
        when = comm_match.group(2).strip()
        state = load_json(state_file, {})
        commitments = state.setdefault("commitments", [])

        commitments.append({
            "id": f"comm_{int(time.time())}",
            "content": comm_desc,
            "when": when,
            "status": "pending"
        })
        save_json(state_file, state)
        msg_text = re.sub(r'\[COMMITMENT:\s*.*?\]', '', msg_text, flags=re.IGNORECASE)

    # 4. CONTEXT (Stress & Timing)
    ctx_match = re.search(r'\[CONTEXT:\s*(.*?)\]', msg_text, re.IGNORECASE)
    if ctx_match:
        ctx_type = ctx_match.group(1).strip()
        state = load_json(state_file, {})

        # Bei Stress sofort einen Cooldown von 4 Stunden einrichten
        cooldown_time = (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat()
        state["current_context"] = {
            "type": ctx_type,
            "detected_at": now_iso,
            "cooldown_until": cooldown_time
        }
        save_json(state_file, state)
        msg_text = re.sub(r'\[CONTEXT:\s*.*?\]', '', msg_text, flags=re.IGNORECASE)

    # 5. SETUP-QUIET (Onboarding: Set quiet hours, e.g. [SETUP-QUIET: 21-07])
    setup_quiet_match = re.search(r'\[SETUP-QUIET:\s*(\d{1,2})-(\d{1,2})\]', msg_text, re.IGNORECASE)
    if setup_quiet_match:
        start_h = int(setup_quiet_match.group(1))
        end_h = int(setup_quiet_match.group(2))
        state = load_json(state_file, {})
        state.setdefault("quiet_hours", {})["start"] = start_h
        state["quiet_hours"]["end"] = end_h
        state["quiet_hours"]["end_minute"] = 0
        save_json(state_file, state)
        log.info(f"Onboarding: quiet_hours set to {start_h:02d}-{end_h:02d}")
        msg_text = re.sub(r'\[SETUP-QUIET:\s*.*?\]', '', msg_text, flags=re.IGNORECASE)

    # 6. SETUP-NOGO (Onboarding: Add topic to no-go list, e.g. [SETUP-NOGO: F1])
    setup_nogo_match = re.search(r'\[SETUP-NOGO:\s*(.*?)\]', msg_text, re.IGNORECASE)
    if setup_nogo_match:
        nogo_topic = setup_nogo_match.group(1).strip().lower()
        state = load_json(state_file, {})
        graph = load_json(GRAPH_FILE, {"interests": {}, "no_go_topics": []})
        if nogo_topic not in graph.get("no_go_topics", []):
            graph.setdefault("no_go_topics", []).append(nogo_topic)
            save_json(GRAPH_FILE, graph)
        log.info(f"Onboarding: no_go_topics added '{nogo_topic}'")
        msg_text = re.sub(r'\[SETUP-NOGO:\s*.*?\]', '', msg_text, flags=re.IGNORECASE)

    # Die Tags sind entfernt, das Sentiment wird jetzt nur anhand des echten Textes berechnet
    args.message = msg_text.strip()
    # ─── ─────────────────────────────────────────────────────────────────────

    history = load_json(HISTORY_FILE, {"pings": []})
    ping = next((p for p in history["pings"] if p["id"] == args.ping_id), None)
    if not ping:
        sys.exit(0)

    topic = ping["topic"]
    delta = decode_sentiment(args.message, args.delay_minutes)
    graph = load_json(GRAPH_FILE, {"interests": {}})

    if topic not in graph.get("interests", {}):
        sys.exit(0)

    # Score updaten
    old_score = graph["interests"][topic]["engagement_score"]
    new_score = round(max(0.0, min(1.0, old_score + delta)), 3)
    graph["interests"][topic]["engagement_score"] = new_score

    # NEU v3: temp_no_go Logik
    temp_no_go = graph.setdefault("temp_no_go", {})
    now_iso = datetime.now(timezone.utc).isoformat()

    if delta > 0:
        # Positive Reaktion → sofort aus Cooldown befreien
        if topic in temp_no_go:
            del temp_no_go[topic]
            log.info(f"Feedback positiv: '{topic}' aus temp_no_go entfernt")
    elif delta <= -0.01:
        # Negative/explizit ablehnende Reaktion → harter Cooldown + Entschuldigung
        if topic not in temp_no_go:
            temp_no_go[topic] = now_iso
            log.info(f"Feedback negativ: '{topic}' → {HARD_NEG_COOLDOWN_H}h Cooldown gesetzt")

        # NEU v4.2: Apology vorbereiten
        state = load_json(state_file, {})
        state["pending_apology"] = True
        save_json(state_file, state)

    save_json(GRAPH_FILE, graph)

    # NEU v4.0: Emotional Context & Stress-Tracking (Phase 2)
    state_file = os.path.join(BASE_DIR, "proaktiv_state.json")
    state = load_json(state_file, {})
    emotional_context = state.setdefault("emotional_context", {"stress_level": 0})

    # Stresslevel anpassen
    current_stress = emotional_context.get("stress_level", 0)
    if delta < 0 or (len(args.message) < 8 and delta <= 0):
        emotional_context["stress_level"] = min(5, current_stress + 1)
    elif delta > 0:
        emotional_context["stress_level"] = max(0, current_stress - 1)

    state["emotional_context"] = emotional_context
    save_json(state_file, state)

    ping["user_reacted"] = True
    ping["reaction_type"] = "positive" if delta > 0 else ("negative" if delta < 0 else "neutral")
    ping["reaction_delta"] = delta
    save_json(HISTORY_FILE, history)

    log.info(
        f"Feedback: topic={topic} | score {old_score} → {new_score} | delta={delta}"
    )

if __name__ == "__main__":
    main()
