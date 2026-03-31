#!/usr/bin/env python3
"""
Proactive v1.0.10 - interest_evolve.py (The Breathing Graph)
Wertet candidate_topics aus, bereitet Promotions vor und lässt alte Themen verblassen.
Sollte 1x nachts per Cronjob laufen.
"""

import json, fcntl, logging, os
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_FILE = os.path.join(BASE_DIR, "interest_graph.json")
STATE_FILE = os.path.join(BASE_DIR, "proaktiv_state.json")
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
LOG_FILE = os.path.join(BASE_DIR, "logs", "proaktiv_cron.log")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
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

def main():
    graph = load_json(GRAPH_FILE, {"interests": {}, "candidate_topics": {}})
    state = load_json(STATE_FILE, {})

    candidates = graph.get("candidate_topics", {})
    interests = graph.get("interests", {})

    now = datetime.now(timezone.utc)
    promoted_keys = []

    # 1. PROMOTION (Ask-First vorbereiten)
    for cand_name, cand_data in candidates.items():
        mentions = cand_data.get("mentions", 0)
        pos_replies = cand_data.get("positive_replies", 0)

        # Heuristik: 3 Erwaehnungen UND mindestens 2 positive Reaktionen
        if mentions >= 3 and pos_replies >= 2:
            log.info(f"Topic-Promotion vorbereitet: {cand_name}")
            state["pending_promotion"] = {
                "topic": cand_name,
                "category": "auto_learned",
                "trigger": f"[SYSTEM-TRIGGER: TOPIC_PROMOTION | candidate={cand_name} | buddy_intent=ask_permission]"
            }
            promoted_keys.append(cand_name)
            break

    for k in promoted_keys:
        del candidates[k]

    # 2. PASSIVE DECAY
    for topic, t_data in interests.items():
        score = t_data.get("engagement_score", 0.5)
        last_date_str = t_data.get("last_topic_date", "")

        if score < 0.2 and last_date_str:
            try:
                last_date = datetime.fromisoformat(last_date_str).replace(tzinfo=timezone.utc)
                if (now - last_date).days > 14:
                    old_prio = t_data.get("priority", 5)
                    t_data["priority"] = max(1, old_prio - 1)
                    log.info(f"Decay angewendet auf: {topic} (Prio jetzt {t_data['priority']})")
            except ValueError:
                pass

    graph["candidate_topics"] = candidates
    save_json(GRAPH_FILE, graph)
    save_json(STATE_FILE, state)

if __name__ == "__main__":
    main()
