#!/usr/bin/env python3
"""
Study Buddy - Deck Manager
Manages flashcard decks with spaced repetition (SM-2 algorithm).

Usage:
    deck_manager.py create <deck_name> --cards '<json_array>'
    deck_manager.py add <deck_name> --cards '<json_array>'
    deck_manager.py list
    deck_manager.py stats <deck_name>
    deck_manager.py review <deck_name>
    deck_manager.py quiz <deck_name> [--count N]
    deck_manager.py exam <deck_name> [--questions N] [--types types]
    deck_manager.py record <deck_name> --card-id <id> --result <correct|partial|missed>
    deck_manager.py due
    deck_manager.py export <deck_name>
    deck_manager.py import <file_path>
    deck_manager.py delete <deck_name>
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

DECKS_DIR = Path.home() / ".openclaw" / "study-buddy" / "decks"


def ensure_dir():
    DECKS_DIR.mkdir(parents=True, exist_ok=True)


def deck_path(name):
    safe = name.lower().replace(" ", "_").replace("/", "_")
    return DECKS_DIR / f"{safe}.json"


def load_deck(name):
    path = deck_path(name)
    if not path.exists():
        print(f"Error: Deck '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def save_deck(deck):
    ensure_dir()
    path = deck_path(deck["name"])
    with open(path, "w") as f:
        json.dump(deck, f, indent=2, ensure_ascii=False)


def new_card(card_id, question, answer):
    return {
        "id": card_id,
        "q": question,
        "a": answer,
        "interval": 0,
        "ease": 2.5,
        "repetitions": 0,
        "next_review": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
    }


def sm2_update(card, result):
    """SM-2 spaced repetition algorithm."""
    ease = card.get("ease", 2.5)
    interval = card.get("interval", 0)
    reps = card.get("repetitions", 0)

    if result == "correct":
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 3
        else:
            interval = int(interval * ease)
        reps += 1
        ease = max(1.3, ease + 0.1)
    elif result == "partial":
        ease = max(1.3, ease - 0.15)
    elif result == "missed":
        reps = 0
        interval = 1
        ease = max(1.3, ease - 0.2)

    card["interval"] = interval
    card["ease"] = round(ease, 2)
    card["repetitions"] = reps
    card["next_review"] = (datetime.now() + timedelta(days=max(interval, 1))).isoformat()
    return card


def cmd_create(args):
    ensure_dir()
    path = deck_path(args.deck_name)
    if path.exists():
        print(f"Error: Deck '{args.deck_name}' already exists. Use 'add' to add cards.", file=sys.stderr)
        sys.exit(1)

    cards_data = json.loads(args.cards)
    cards = [new_card(i + 1, c["q"], c["a"]) for i, c in enumerate(cards_data)]

    deck = {
        "name": args.deck_name,
        "cards": cards,
        "next_id": len(cards) + 1,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    save_deck(deck)
    print(json.dumps({"status": "created", "deck": args.deck_name, "cards": len(cards)}, indent=2))


def cmd_add(args):
    deck = load_deck(args.deck_name)
    cards_data = json.loads(args.cards)
    next_id = deck.get("next_id", len(deck["cards"]) + 1)

    new_cards = []
    for i, c in enumerate(cards_data):
        new_cards.append(new_card(next_id + i, c["q"], c["a"]))

    deck["cards"].extend(new_cards)
    deck["next_id"] = next_id + len(new_cards)
    deck["updated_at"] = datetime.now().isoformat()
    save_deck(deck)
    print(json.dumps({"status": "added", "deck": args.deck_name, "new_cards": len(new_cards), "total_cards": len(deck["cards"])}, indent=2))


def cmd_list(args):
    ensure_dir()
    decks = []
    for f in sorted(DECKS_DIR.glob("*.json")):
        with open(f) as fh:
            d = json.load(fh)
            now = datetime.now()
            due = sum(1 for c in d["cards"] if datetime.fromisoformat(c["next_review"]) <= now)
            decks.append({
                "name": d["name"],
                "cards": len(d["cards"]),
                "due": due,
                "created": d.get("created_at", "unknown"),
            })
    print(json.dumps({"decks": decks}, indent=2))


def cmd_stats(args):
    deck = load_deck(args.deck_name)
    now = datetime.now()
    cards = deck["cards"]
    due = [c for c in cards if datetime.fromisoformat(c["next_review"]) <= now]
    mastered = [c for c in cards if c.get("repetitions", 0) >= 5]
    learning = [c for c in cards if 0 < c.get("repetitions", 0) < 5]
    new = [c for c in cards if c.get("repetitions", 0) == 0]

    print(json.dumps({
        "deck": args.deck_name,
        "total_cards": len(cards),
        "due_now": len(due),
        "mastered": len(mastered),
        "learning": len(learning),
        "new": len(new),
        "average_ease": round(sum(c.get("ease", 2.5) for c in cards) / max(len(cards), 1), 2),
    }, indent=2))


def cmd_review(args):
    deck = load_deck(args.deck_name)
    now = datetime.now()
    due = [c for c in deck["cards"] if datetime.fromisoformat(c["next_review"]) <= now]

    if not due:
        next_reviews = sorted(deck["cards"], key=lambda c: c["next_review"])
        next_time = next_reviews[0]["next_review"] if next_reviews else "never"
        print(json.dumps({"status": "no_cards_due", "next_review": next_time}, indent=2))
        return

    random.shuffle(due)
    cards_out = [{"id": c["id"], "q": c["q"], "a": c["a"], "repetitions": c.get("repetitions", 0)} for c in due]
    print(json.dumps({"deck": args.deck_name, "due_count": len(due), "cards": cards_out}, indent=2))


def cmd_quiz(args):
    deck = load_deck(args.deck_name)
    count = min(args.count or 10, len(deck["cards"]))
    selected = random.sample(deck["cards"], count)
    cards_out = [{"id": c["id"], "q": c["q"], "a": c["a"]} for c in selected]
    print(json.dumps({"deck": args.deck_name, "quiz_count": count, "cards": cards_out}, indent=2))


def cmd_exam(args):
    deck = load_deck(args.deck_name)
    count = min(args.questions or 20, len(deck["cards"]))
    types = (args.types or "multiple_choice,short_answer,true_false").split(",")
    selected = random.sample(deck["cards"], count)
    all_answers = [c["a"] for c in deck["cards"]]

    questions = []
    for i, card in enumerate(selected):
        q_type = types[i % len(types)]
        q = {"number": i + 1, "type": q_type, "question": card["q"], "card_id": card["id"]}

        if q_type == "multiple_choice":
            distractors = [a for a in all_answers if a != card["a"]]
            random.shuffle(distractors)
            options = [card["a"]] + distractors[:3]
            random.shuffle(options)
            q["options"] = options
            q["correct"] = card["a"]
        elif q_type == "true_false":
            use_true = random.choice([True, False])
            if use_true:
                q["statement"] = card["a"]
                q["correct"] = True
            else:
                if distractors := [a for a in all_answers if a != card["a"]]:
                    q["statement"] = random.choice(distractors)
                else:
                    q["statement"] = card["a"]
                    use_true = True
                q["correct"] = use_true
        else:
            q["correct"] = card["a"]

        questions.append(q)

    print(json.dumps({"deck": args.deck_name, "exam": questions}, indent=2))


def cmd_record(args):
    deck = load_deck(args.deck_name)
    card_id = args.card_id

    for card in deck["cards"]:
        if card["id"] == card_id:
            sm2_update(card, args.result)
            deck["updated_at"] = datetime.now().isoformat()
            save_deck(deck)
            print(json.dumps({
                "status": "recorded",
                "card_id": card_id,
                "result": args.result,
                "next_review": card["next_review"],
                "interval_days": card["interval"],
                "ease": card["ease"],
            }, indent=2))
            return

    print(f"Error: Card ID {card_id} not found in deck '{args.deck_name}'.", file=sys.stderr)
    sys.exit(1)


def cmd_due(args):
    ensure_dir()
    now = datetime.now()
    results = []
    for f in sorted(DECKS_DIR.glob("*.json")):
        with open(f) as fh:
            d = json.load(fh)
            due = [c for c in d["cards"] if datetime.fromisoformat(c["next_review"]) <= now]
            if due:
                results.append({"deck": d["name"], "due_count": len(due)})
    print(json.dumps({"due_decks": results, "total_due": sum(r["due_count"] for r in results)}, indent=2))


def cmd_export(args):
    deck = load_deck(args.deck_name)
    print(json.dumps(deck, indent=2, ensure_ascii=False))


def cmd_import(args):
    ensure_dir()
    with open(args.file_path) as f:
        deck = json.load(f)
    if "name" not in deck or "cards" not in deck:
        print("Error: Invalid deck format. Must have 'name' and 'cards'.", file=sys.stderr)
        sys.exit(1)
    save_deck(deck)
    print(json.dumps({"status": "imported", "deck": deck["name"], "cards": len(deck["cards"])}, indent=2))


def cmd_delete(args):
    path = deck_path(args.deck_name)
    if not path.exists():
        print(f"Error: Deck '{args.deck_name}' not found.", file=sys.stderr)
        sys.exit(1)
    path.unlink()
    print(json.dumps({"status": "deleted", "deck": args.deck_name}, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Study Buddy - Flashcard Deck Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("create")
    p.add_argument("deck_name")
    p.add_argument("--cards", required=True)

    p = sub.add_parser("add")
    p.add_argument("deck_name")
    p.add_argument("--cards", required=True)

    sub.add_parser("list")

    p = sub.add_parser("stats")
    p.add_argument("deck_name")

    p = sub.add_parser("review")
    p.add_argument("deck_name")

    p = sub.add_parser("quiz")
    p.add_argument("deck_name")
    p.add_argument("--count", type=int, default=10)

    p = sub.add_parser("exam")
    p.add_argument("deck_name")
    p.add_argument("--questions", type=int, default=20)
    p.add_argument("--types", default="multiple_choice,short_answer,true_false")

    p = sub.add_parser("record")
    p.add_argument("deck_name")
    p.add_argument("--card-id", type=int, required=True)
    p.add_argument("--result", required=True, choices=["correct", "partial", "missed"])

    sub.add_parser("due")

    p = sub.add_parser("export")
    p.add_argument("deck_name")

    p = sub.add_parser("import")
    p.add_argument("file_path")

    p = sub.add_parser("delete")
    p.add_argument("deck_name")

    args = parser.parse_args()

    commands = {
        "create": cmd_create, "add": cmd_add, "list": cmd_list,
        "stats": cmd_stats, "review": cmd_review, "quiz": cmd_quiz,
        "exam": cmd_exam, "record": cmd_record, "due": cmd_due,
        "export": cmd_export, "import": cmd_import, "delete": cmd_delete,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
