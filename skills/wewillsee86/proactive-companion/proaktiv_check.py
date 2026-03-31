#!/usr/bin/env python3
"""
Proactive v1.0.35 - proaktiv_check.py
Changelog v1.0.35 (2026-03-31):
 + FIX: Early exit on Quiet Hours — zero token cost during off-hours
Changelog v1.0.34 (2026-03-31):
 + FIX: Cron --session isolated --no-deliver (kein Main-Chat-Spam)
Changelog v1.0.33 (2026-03-31):
 + FIX: get_session_id() exakt nach Spezifikation
Changelog v1.0.28 (2026-03-31):
 + RELEASE CANDIDATE: Dynamic UUID lookup, explicit routing, blocking run
 + install.sh: dual-language UX Hinweis
Changelog v1.0.23 (2026-03-31):
 + BUGFIX: Fixed split-brain amnesia (feste Verdrahtung)
Changelog v1.0.21 (2026-03-31):
 + BUGFIX: Restored explicit telegram routing flags
Changelog v1.0.19 (2026-03-31):
 + STRICT SILENCE POLICY: kein Fallback mehr
Changelog v1.0.10 (2026-03-30):
 + Daily Interest Evolution (interest_evolve) direkt eingebaut
 + Runs once per day (bei erstem Cron-Durchlauf nach Mitternacht)
 + Calls interest_evolve.main(), State wird neu geladen nach Promotion
 + FIX: BASE before import, TELEGRAM_NR aus Env Var (keine Hard-coded IDs)
"""

import json, random, logging, sys, os, subprocess, time, uuid
from datetime import datetime, date, timedelta
import fcntl
import importlib.util

# BASE must be defined FIRST, before loading interest_evolve
# Dynamic BASE_DIR — portable, works on any OpenClaw installation
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "proaktiv_state.json")
HISTORY_FILE = os.path.join(BASE_DIR, "ping_history.json")
GRAPH_FILE = os.path.join(BASE_DIR, "interest_graph.json")
SOCIAL_FILE = os.path.join(BASE_DIR, "social_knowledge.json")
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
LOG_FILE = os.path.join(BASE_DIR, "logs", "proaktiv_cron.log")

# TELEGRAM_NR: MUST be set via environment — no fallback allowed
_tg = os.environ.get("OPENCLAW_TELEGRAM_NR", "")
if not _tg:
    raise RuntimeError("KRITISCH: OPENCLAW_TELEGRAM_NR nicht gesetzt! Bitte in .env eintragen.")
TELEGRAM_NR = _tg

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Europe/Berlin")
except (ImportError, KeyError):
    from datetime import timezone, timedelta as td
    import time as _t
    _dst = _t.daylight and _t.localtime().tm_isdst
    TZ = timezone(td(hours=2 if _dst else 1))

# Load interest_evolve as module (daily gardener) — BASE must be defined above first!
_spec = importlib.util.spec_from_file_location(
    "interest_evolve", os.path.join(BASE_DIR, "interest_evolve.py")
)
interest_evolve = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(interest_evolve)

QUIET_START = 21
QUIET_END_H = 8
QUIET_END_M = 30
MORNING_UNTIL = 10
PRESSURE_STEP = 30
PRESSURE_MAX = 90
HISTORY_MAX = 30

# Dormant-Automatik: nach N ignorierten Pings → Cooldown
IGNORE_THRESHOLD = 3
IGNORE_COOLDOWN_H = 48
PASSIVE_DECAY_RATE = 0.003

# ─── v3.1 NEU: Arbeitszeiten-Schutz ────────────────────────────────────────
WORK_DAYS = {0, 1, 2, 3, 4, 5}  # Montag bis Samstag
WORK_HOUR_START = 8
WORK_HOUR_END = 17              # Schutzschild gilt bis 16:59 Uhr

def is_work_hours(now=None) -> bool:
    """True wenn Mo–Sa zwischen 08:00 und 17:00 Uhr (Europe/Berlin)."""
    if now is None:
        now = datetime.now(TZ)
    return (
        now.weekday() in WORK_DAYS
        and WORK_HOUR_START <= now.hour < WORK_HOUR_END
    )

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger()

# ─── JSON-Helfer ────────────────────────────────────────────────────────────

def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        with open(path, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)
        if isinstance(default, dict):
            for k, v in default.items():
                data.setdefault(k, v)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return default.copy() if isinstance(default, dict) else default

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

def days_since(date_str):
    if not date_str:
        return 999
    try:
        return (date.today() - datetime.fromisoformat(date_str).date()).days
    except ValueError:
        return 999

# ─── NEU v3: Letzter Chat-Kontext ───────────────────────────────────────────

def get_session_id() -> str:
    _tg = os.environ.get("OPENCLAW_TELEGRAM_NR", "")
    if not _tg:
        raise RuntimeError("KRITISCH: OPENCLAW_TELEGRAM_NR nicht gesetzt.")
    res = subprocess.run(
        ["openclaw", "sessions", "--json"],
        capture_output=True, text=True, timeout=10
    )
    data = json.loads(res.stdout)
    sessions = data.get("sessions", [])
    for s in sessions:
        if isinstance(s, dict) and s.get("key") == f"agent:main:telegram:direct:{_tg}":
            return s["sessionId"]
    raise RuntimeError("[ERROR] Keine Telegram-Session gefunden. Bitte zuerst eine Nachricht an den Bot senden.")

def get_last_chat_context() -> str:
    """
    Holt die letzte User-Nachricht aus der OpenClaw-Session.
    Gibt einen kurzen String zurück (max 120 Zeichen) oder leer.
    """
    try:
        sid = get_session_id()
        res = subprocess.run(
            ["openclaw", "history", "--session-id", sid, "--last", "5", "--json"],
            capture_output=True, text=True, timeout=10
        )
        if res.returncode != 0:
            return ""
        data = json.loads(res.stdout)
        messages = data.get("messages", [])
        user_msgs = [
            m["content"] for m in messages
            if m.get("role") == "user" and m.get("content")
        ]
        if user_msgs:
            last = user_msgs[-1].strip()[:120]
            return last.replace('"', "'").replace("|", "/")
        return ""
    except Exception as e:
        log.warning(f"get_last_chat_context Fehler: {e}")
        return ""

# ─── v3.1: Passive Decay – broadcast-aware ──────────────────────────────────

def apply_passive_decay(graph: dict, history: dict):
    """
    Senkt engagement_score für ignorierte Pings.

    Ausnahmen (KEIN Decay):
    - message_type == "broadcast": Lesen ohne Antwort ist erwünscht
    - Ping fiel in Arbeitszeiten (is_work_hours war True zum Ping-Zeitpunkt)
    """
    cutoff = datetime.now(TZ) - timedelta(hours=24)
    ignored_topics: set = set()

    for ping in history.get("pings", []):
        try:
            ts = datetime.fromisoformat(ping["timestamp"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=TZ)
        except Exception:
            continue

        if not (ts > cutoff and ping.get("delivered") and not ping.get("daniel_reacted")):
            continue

        topic = ping.get("topic", "")
        mtype = graph.get("interests", {}).get(topic, {}).get("message_type", "dialog")

        # Broadcast: niemals bestrafen
        if mtype == "broadcast":
            continue

        # Dialog während Arbeitszeit: Pause respektieren
        if is_work_hours(ts):
            log.info(f"PassiveDecay: '{topic}' übersprungen (Arbeitszeit-Schutz)")
            continue

        ignored_topics.add(topic)

    changed = False
    for topic in ignored_topics:
        if topic in graph.get("interests", {}):
            old = graph["interests"][topic]["engagement_score"]
            new = round(max(0.1, old - PASSIVE_DECAY_RATE), 3)
            if new != old:
                graph["interests"][topic]["engagement_score"] = new
                changed = True
                log.info(f"PassiveDecay: {topic} {old} → {new}")

    if changed:
        save_json(GRAPH_FILE, graph)

# ─── v3.1: Dormant-Automatik – broadcast-aware ──────────────────────────────

def apply_dormant_automatik(graph: dict, history: dict):
    """
    3x consecutive ignore → 48h temp_no_go.

    Ausnahmen:
    - message_type == "broadcast": nie in Cooldown
    - Ping fiel in Arbeitszeit: zählt nicht als "ignore" für den Zähler
    """
    pings = history.get("pings", [])
    now = datetime.now(TZ)

    topic_stats: dict = {}
    for ping in reversed(pings[-20:]):
        topic = ping.get("topic", "")
        if not topic:
            continue

        mtype = graph.get("interests", {}).get(topic, {}).get("message_type", "dialog")
        if mtype == "broadcast":
            continue

        if topic not in topic_stats:
            topic_stats[topic] = {"consec_ignored": 0, "had_reaction": False}

        if ping.get("daniel_reacted"):
            topic_stats[topic]["had_reaction"] = True
        elif ping.get("delivered") and not topic_stats[topic]["had_reaction"]:
            # Arbeitszeit-Schutz: Ping in Arbeitszeit → kein Ignore-Zähler
            try:
                ts = datetime.fromisoformat(ping["timestamp"])
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=TZ)
                if is_work_hours(ts):
                    log.info(f"DormantCheck: '{topic}' ignore in Arbeitszeit – übersprungen")
                    continue
            except Exception:
                pass
            topic_stats[topic]["consec_ignored"] += 1

    temp_no_go = graph.setdefault("temp_no_go", {})
    changed = False

    for topic, stats in topic_stats.items():
        if stats["consec_ignored"] >= IGNORE_THRESHOLD and not stats["had_reaction"]:
            if topic not in temp_no_go:
                temp_no_go[topic] = now.isoformat()
                log.info(
                    f"DORMANT-AUTOMATIK: '{topic}' → {IGNORE_COOLDOWN_H}h Cooldown "
                    f"({stats['consec_ignored']}x außerhalb Arbeitszeit ignoriert)"
                )
                changed = True

    # Abgelaufene Cooldowns entfernen
    for topic in list(temp_no_go.keys()):
        try:
            added_at = datetime.fromisoformat(temp_no_go[topic])
            if added_at.tzinfo is None:
                added_at = added_at.replace(tzinfo=TZ)
        except Exception:
            del temp_no_go[topic]; changed = True; continue
        if (now - added_at).total_seconds() > IGNORE_COOLDOWN_H * 3600:
            log.info(f"DORMANT-AUTOMATIK: '{topic}' reaktiviert")
            del temp_no_go[topic]; changed = True

    if changed:
        save_json(GRAPH_FILE, graph)

# ─── Topic-Selektion ───────────────────────────────────────────────────────

def decide_next_ping(now):
    graph = load_json(GRAPH_FILE, {"interests": {}, "no_go_topics": []})
    history = load_json(HISTORY_FILE, {"pings": []})
    hour = now.hour
    recent = [p["topic"] for p in history["pings"][-5:]]

    # Passive Decay + Dormant-Automatik bei jeder Selektion updaten
    apply_passive_decay(graph, history)
    apply_dormant_automatik(graph, history)

    temp_no_go = set(graph.get("temp_no_go", {}).keys())
    no_go = set(graph.get("no_go_topics", []))

    candidates = []
    for topic, data in graph["interests"].items():
        if topic in no_go or topic in temp_no_go:
            log.info(f"decide_next_ping: '{topic}' übersprungen (no_go/temp_no_go)")
            continue

        score = data.get("engagement_score", 0.5)
        if score < 0.2:
            dormant = graph.setdefault("dormant", {})
            if topic not in dormant:
                dormant[topic] = str(date.today())
                save_json(GRAPH_FILE, graph)
            continue

        tw = data.get("time_window", {"from": 9, "to": 22})
        if not (tw["from"] <= hour < tw["to"]):
            continue

        # F1 Ruhezone am Sonntag (SOUL.md: "SO: RUHEMODUS — kein F1-Ping")
        if topic == "f1" and now.weekday() == 6:
            log.info(f"decide_next_ping: f1 übersprungen (Sonntag = Ruhezone)")
            continue

        if recent.count(topic) >= 2:
            continue

        priority = data.get("priority", 5)
        last_date = data.get("last_topic_date") or data.get("last_session", "")
        days_idle = days_since(last_date)
        urgency = (
            priority * 0.4
            + score * 0.4
            + min(days_idle, 7) / 7 * 0.2 * 10
        )
        candidates.append({"topic": topic, "urgency": round(urgency, 2), "data": data})

    if not candidates:
        return {"topic": "motivation", "urgency": 1, "data": {}}

    candidates.sort(key=lambda x: x["urgency"], reverse=True)
    winner = candidates[0]
    log.info(f"decide_next_ping: {winner['topic']} (urgency={winner['urgency']})")
    return winner

# ─── v3.1: Trigger aufbauen ─────────────────────────────────────────────────

def build_trigger(ping: dict, ping_id: str, hours_silent: float = 0.0) -> str:
    """
    Baut den System-Trigger-String.

    v3.1:
    - Broadcast-Topics: message_type im Trigger übergeben
    - Dialog-Topics: last_chat-Kontext aus Session
    """
    topic = ping["topic"].upper()
    data = ping.get("data", {})

    parts = [f"[SYSTEM-TRIGGER: {topic}"]

    field_map = {
        "last_topic": "last_topic",
        "last_verb": "last_verb",
        "current_project": "project",
        "last_session": "last_session",
    }
    for field, label in field_map.items():
        val = data.get(field)
        if val:
            parts.append(f"{label}={val}")

    score = data.get("engagement_score")
    if score is not None:
        parts.append(f"engagement={score:.0%}")

    mtype = data.get("message_type", "dialog")
    parts.append(f"message_type={mtype}")

    # Dialog-Modus → Kontext aus letztem Chat holen
    if mtype != "broadcast":
        last_chat = get_last_chat_context()
        if last_chat:
            parts.append(f'last_chat="{last_chat}"')
        else:
            parts.append("last_chat=unbekannt")

    if ping["topic"] == "followup":
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        parts.append(f"memory_date={yesterday}")
    if hours_silent > 1:
        parts.append(f"hours_silent={hours_silent:.1f}h")

    # NEU v4.0: Memory Refresh Loop (Phase 1)
    state = load_json(STATE_FILE, {})
    buddy_profile = state.get("buddy_profile", {})
    last_refresh = buddy_profile.get("last_memory_refresh", "")

    # Alle 7 Tage besteht eine 15% Chance auf einen Memory Refresh (nur bei Dialog-Topics)
    if mtype != "broadcast" and days_since(last_refresh) > 7 and random.random() < 0.15:
        social_db = load_json(SOCIAL_FILE, {"people": {}})
        people_keys = list(social_db.get("people", {}).keys())

        if people_keys:
            random_person_key = random.choice(people_keys)
            person_data = social_db["people"][random_person_key]
            facts = person_data.get("key_facts", [])

            if facts:
                random_fact = random.choice(facts)
                fact_name = random_fact.get("fact", "unbekannt")
                fact_value = random_fact.get("value", "unbekannt")

                parts.append(f'buddy_intent="memory_refresh"')
                parts.append(f'memory_refresh_fact="{random_person_key}:{fact_name}:{fact_value}"')

                # State updaten, damit der Cooldown von 7 Tagen wieder greift
                buddy_profile["last_memory_refresh"] = str(date.today())
                state["buddy_profile"] = buddy_profile
                save_json(STATE_FILE, state)

    # NEU v4.0: Contextual Humor & Wellness (Phase 2)
    emotional_context = state.get("emotional_context", {"stress_level": 0})
    stress_level = emotional_context.get("stress_level", 0)
    humor_allowed_topics = ["suno", "f1", "ki_news"]

    # Humor nur bei Erlaubnis und niedrigem Stress
    if stress_level <= 1 and topic.lower() in humor_allowed_topics:
        parts.append('humor_hint="subtle"')

    # Bei anhaltendem Stress (Level >= 3) auf Behutsamkeit schalten
    elif stress_level >= 3 and mtype != "broadcast":
        parts.append('buddy_intent="wellness"')

    # NEU v4.0: Progressive Disclosure (Phase 3)
    # Je höher der Engagement-Score, desto tiefer darf Neo ins Detail gehen
    current_score = data.get("engagement_score", 0.5)
    if current_score > 0.65:
        parts.append('disclosure_level="deep"')
    else:
        parts.append('disclosure_level="basic"')

    # NEU v4.0: Ambient Awareness (Phase 3)
    # Neo ein Gefühl für Feierabend und Wochenende geben
    now_ambient = datetime.now(TZ)
    if now_ambient.weekday() >= 5:
        parts.append('ambient_context="weekend"')
    elif now_ambient.hour >= 18:
        parts.append('ambient_context="evening_chill"')
    else:
        parts.append('ambient_context="workday"')

    parts.append(f"ping_id={ping_id}")
    return " | ".join(parts) + "]"

# ─── Trigger injizieren ──────────────────────────────────────────────────────

def get_latest_telegram_session():
    """
    Holt dynamisch die aktuellste Telegram-Direct Session-UUID und User-ID.
    v1.0.28: Löst die feste Verdrahtung ab — Split-Brain-Fix durch echte UUID-Lookup.
    """
    try:
        result = subprocess.run(
            ["openclaw", "sessions", "--json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            print(f"[ERROR] Fehler beim Abrufen der Sessions: {result.stderr}")
            return None, None

        sessions = json.loads(result.stdout)

        # Nur telegram:direct Sessions filtern
        tg_sessions = [s for s in sessions if "telegram:direct" in s.get("key", "")]

        if not tg_sessions:
            print("[WARN] Keine Telegram-Session gefunden. Der User muss zuerst 1x auf Telegram schreiben!")
            return None, None

        # Nach Aktualität sortieren (neueste zuerst)
        tg_sessions.sort(key=lambda x: x.get("updatedAt", 0), reverse=True)
        best_session = tg_sessions[0]

        session_uuid = best_session.get("sessionId")
        telegram_user_id = best_session.get("key", "").split(":")[-1]

        return session_uuid, telegram_user_id

    except Exception as e:
        print(f"[ERROR] Exception beim Session-Lookup: {e}")
        return None, None


def inject_trigger(trigger_text: str) -> bool:
    """
    v1.0.28: Dynamischer UUID-Lookup mit explizitem Telegram-Routing.
   -split-Brain-Fix: Offene Session-UUID via openclaw sessions --json,
    dann --reply-channel telegram --reply-to <id> fuer sauberes Delivery.
    """
    session_uuid, tg_nr = get_latest_telegram_session()

    if not session_uuid or not tg_nr:
        print("[ERROR] Keine Telegram-Session gefunden. Bitte zuerst eine Nachricht an den Bot senden.")
        log.error("Trigger-Injection fehlgeschlagen. Breche ab (Strict Silence).")
        return False

    cmd = [
        "openclaw", "agent",
        "--session-id", session_uuid,
        "--message", trigger_text,
        "--deliver",
        "--reply-channel", "telegram",
        "--reply-to", tg_nr
    ]

    print(f"[INFO] Injiziere in Telegram Session UUID: {session_uuid} für User: {tg_nr}")
    log.info(f"inject_trigger: UUID={session_uuid[:16]}...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("[INFO] Trigger erfolgreich via UUID injiziert!")
            return True
        else:
            print(f"[ERROR] Injection fehlgeschlagen: {result.stderr}")
            log.error(f"Trigger-Injection fehlgeschlagen. Breche ab (Strict Silence).")
            return False
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout beim Injecting des Triggers.")
        log.error("Trigger-Injection Timeout. Breche ab (Strict Silence).")
        return False

# ─── Main Loop ─────────────────────────────────────────────────────────────────

DEFAULT_STATE = {
    "ping_pressure": 0,
    "daily_budget_used": 0,
    "last_morning_ping_date": "",
    "last_budget_reset_date": "",
    "last_evolve_date": "",
    "last_run_date": "",
    "last_user_message_ts": 0,
    "active_session_id": "",  # Written by feedback_update.py, read by inject_trigger
}

def main():
    now = datetime.now(TZ)
    today = str(date.today())
    hour = now.hour
    minute = now.minute

    # Früher Exit bei Quiet Hours — keine API-Calls, keine Token-Kosten
    if hour >= QUIET_START or hour < QUIET_END_H:
        logging.info(f"Quiet Hours aktiv ({hour}h) — Exit ohne API-Calls.")
        sys.exit(0)

    DAILY_BUDGET = 10 if now.weekday() >= 5 else 8
    log.info(f"=== Proaktiv-Check v4.2 | {now.strftime('%Y-%m-%d %H:%M')} CET ===")

    state = load_json(STATE_FILE, DEFAULT_STATE)

    # ─── NEU v4.2: Täglicher Gärtner (Interest Evolution Trigger) ─────────
    today_str = str(now.date())
    if state.get("last_evolve_date") != today_str:
        log.info("Neuer Tag erkannt: Führe Interest Evolution (Gärtner) aus...")
        try:
            interest_evolve.main()
        except Exception as e:
            log.error(f"Fehler bei interest_evolve: {e}")

        # State neu laden, da interest_evolve ihn verändert haben könnte (Promotions!)
        state = load_json(STATE_FILE, DEFAULT_STATE)
        state["last_evolve_date"] = today_str
        save_json(STATE_FILE, state)
        log.info("Interest Evolution abgeschlossen.")
    # ─────────────────────────────────────────────────────────────────────────

    # Tages-Budget-Reset
    if state["last_budget_reset_date"] != today:
        state["daily_budget_used"] = 0
        state["last_budget_reset_date"] = today
        log.info("Budget zurückgesetzt.")

    if state["daily_budget_used"] >= DAILY_BUDGET:
        log.info("Budget erschöpft.")
        save_json(STATE_FILE, state)
        sys.exit(0)

    # Quiet Hours
    in_quiet = (
        hour >= QUIET_START
        or hour < QUIET_END_H
        or (hour == QUIET_END_H and minute < QUIET_END_M)
    )
    if in_quiet:
        # ─── NEU v5: Die Nachtschicht (Memory Cleanup) ───────────────────────
        today_str = str(now.date())
        if state.get("last_nightshift") != today_str:
            log.info("Quiet Hours aktiv. Starte lautlose Nachtschicht (Memory Cleanup)...")
            try:
                subprocess.run([
                    "openclaw", "send",
                    "[SYSTEM-NIGHTSHIFT: CLEANUP] Führe deine nächtliche Memory-Compaction durch.",
                    "--session", "isolated"
                ], check=True, capture_output=True)
                state["last_nightshift"] = today_str
                save_json(STATE_FILE, state)
                log.info("Nachtschicht erfolgreich gezündet.")
            except Exception as e:
                log.error(f"Fehler bei der Nachtschicht-Zündung: {e}")
        else:
            log.info("Quiet Hours aktiv. Nachtschicht bereits erledigt. Kurama schläft.")
        sys.exit(0)
        # ─────────────────────────────────────────────────────────────────────────

    # Morgen-Garantie
    after_quiet = hour > QUIET_END_H or (hour == QUIET_END_H and minute >= QUIET_END_M)
    in_morning = after_quiet and hour < MORNING_UNTIL
    morning_done = state["last_morning_ping_date"] == today

    if in_morning and not morning_done:
        log.info("Morgen-Garantie.")
        last_chat = get_last_chat_context()
        ctx_part = f' | last_chat="{last_chat}"' if last_chat else ""
        ping_id = str(uuid.uuid4())[:8]
        trigger = f"[SYSTEM-TRIGGER: MORGEN-BRIEFING{ctx_part} | ping_id={ping_id}]"
        state["ping_pressure"] = 0
        state["last_morning_ping_date"] = today
        state["daily_budget_used"] += 1
        save_json(STATE_FILE, state)
        if not inject_trigger(trigger):
            log.error("KRITISCH: Morgen-Briefing fehlgeschlagen!")
        sys.exit(0)

    # Druckkessel
    pressure = state["ping_pressure"]
    roll = random.randint(0, 100)
    log.info(f"Druckkessel | pressure={pressure}% | roll={roll}")

    if roll > pressure:
        state["ping_pressure"] = min(PRESSURE_MAX, pressure + PRESSURE_STEP)
        log.info(f"Fail → Druck {state['ping_pressure']}%.")
        save_json(STATE_FILE, state)
        sys.exit(0)

    # Silence-Breaker: hours_silent berechnen
    last_ts = state.get("last_user_message_ts", 0)
    hours_silent = 0.0
    if last_ts > 0:
        hours_silent = (now.timestamp() - last_ts) / 3600

    # ─── NEU v4.2: COMPANION LAYER (Phase 3) ─────────────────────────────────
    ping_id = str(uuid.uuid4())[:8]
    special_trigger = None
    companion_topic = "companion"

    # State laden für Companion-Checks
    state = load_json(STATE_FILE, {})
    now_date_str = str(now.date())

    # 1. Adaptive Apology (Höchste Priorität)
    if state.get("pending_apology"):
        special_trigger = f"[SYSTEM-TRIGGER: APOLOGY | buddy_intent=apologize_and_adjust | ping_id={ping_id}]"
        state["pending_apology"] = None
        companion_topic = "apology"

    # 2. Commitment Follow-up (Offene Versprechen abarbeiten)
    elif "commitments" in state:
        for c in state["commitments"]:
            if c.get("status") == "pending":
                special_trigger = f"[SYSTEM-TRIGGER: COMMITMENT_FOLLOWUP | content=\"{c['content']}\" | buddy_intent=followup_commitment | ping_id={ping_id}]"
                c["status"] = "done"  # Nur einmal triggern
                companion_topic = "commitment"
                break

    # 3. Goal Check-in
    elif not special_trigger and "goals" in state:
        for g_id, g in state["goals"].items():
            if g.get("status") == "active" and g.get("next_checkin") == now_date_str:
                special_trigger = f"[SYSTEM-TRIGGER: GOAL_CHECKIN | goal=\"{g['description']}\" | deadline=\"{g['deadline']}\" | buddy_intent=goal_checkin | ping_id={ping_id}]"
                g["next_checkin"] = None  # Warten auf neues Datum durch LLM
                companion_topic = "goal"
                break

    # 4. Topic Promotion (Vom interest_evolve.py vorbereitet)
    elif not special_trigger and state.get("pending_promotion"):
        promo = state["pending_promotion"]
        special_trigger = f"{promo['trigger']} | ping_id={ping_id}]"
        companion_topic = promo["topic"]
        state["pending_promotion"] = None

    # --- ENTSCHEIDUNG ---
    if special_trigger:
        # Wir feuern einen Companion-Trigger
        trigger = special_trigger.replace("] |", " |")  # Clean up if needed
        ping = {"topic": companion_topic, "urgency": 6.0}  # Fake-Ping für die History
        save_json(STATE_FILE, state)
        log.info(f"Companion Layer aktiv: {companion_topic}")
    else:
        # Normaler Flow
        ping = decide_next_ping(now)
        trigger = build_trigger(ping, ping_id, hours_silent=hours_silent)

        # 5. Serendipity Engine (10% Chance bei normalen Pings)
        if random.random() < 0.10:
            trigger = trigger.replace("]", " | buddy_intent=serendipity]")
            log.info("Serendipity Engine getriggert!")
    # ─────────────────────────────────────────────────────────────────────────

    state["ping_pressure"] = 0
    state["daily_budget_used"] += 1
    save_json(STATE_FILE, state)

    # Ping in History speichern
    history = load_json(HISTORY_FILE, {"pings": []})
    history["pings"].append({
        "id": ping_id,
        "timestamp": now.isoformat(),
        "topic": ping["topic"],
        "urgency": ping["urgency"],
        "delivered": False,
        "daniel_reacted": False,
        "reaction_type": None,
        "reaction_delta": None,
    })
    history["pings"] = history["pings"][-HISTORY_MAX:]
    save_json(HISTORY_FILE, history)

    log.info(f"→ {trigger[:120]} | Budget: {state['daily_budget_used']}/{DAILY_BUDGET}")

    if inject_trigger(trigger):
        history["pings"][-1]["delivered"] = True
        save_json(HISTORY_FILE, history)
    else:
        # STRICT SILENCE POLICY v1.0.19: Kein Fallback, keine Direkt-Nachricht.
        # Bei Inject-Fehler: nur loggen, dann Schweigen.
        log.error("Trigger-Injection fehlgeschlagen. Breche ab (Strict Silence).")

    # last_run_date aktualisieren
    state["last_run_date"] = today
    save_json(STATE_FILE, state)

if __name__ == "__main__":
    main()
