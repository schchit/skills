#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote
from urllib.request import Request, urlopen

KMB_BASE = "https://data.etabus.gov.hk/v1/transport/kmb"
CITYBUS_BASE = "https://rt.data.gov.hk/v2/transport/citybus"
TZ = ZoneInfo("Asia/Hong_Kong")

KMB_LIKE_OPERATORS = {"kmb", "lwb"}
CITYBUS_OPERATORS = {"citybus", "ctb"}


def fetch_json(url: str):
    req = Request(url, headers={"User-Agent": "OpenClaw hk-bus-eta skill"})
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize_operator(operator: str) -> str:
    op = (operator or "kmb").strip().lower()
    if op in KMB_LIKE_OPERATORS:
        return op
    if op in CITYBUS_OPERATORS:
        return "citybus"
    raise ValueError(f"Unsupported operator: {operator}")


def normalize_direction(direction: str, operator: str) -> str:
    direction = (direction or "both").strip().lower()
    if direction not in {"inbound", "outbound", "both"}:
        raise ValueError(f"Unsupported direction: {direction}")
    if direction == "both":
        return direction
    if operator == "citybus":
        return "inbound" if direction == "inbound" else "outbound"
    return direction


def get_route_stops(operator: str, route: str, direction: str, service_type: str):
    if operator in KMB_LIKE_OPERATORS:
        url = f"{KMB_BASE}/route-stop/{quote(route)}/{direction}/{service_type}"
        return fetch_json(url)["data"]

    url = f"{CITYBUS_BASE}/route-stop/CTB/{quote(route)}/{direction}"
    return fetch_json(url)["data"]


def get_stop(operator: str, stop_id: str):
    if operator in KMB_LIKE_OPERATORS:
        return fetch_json(f"{KMB_BASE}/stop/{stop_id}")["data"]
    return fetch_json(f"{CITYBUS_BASE}/stop/{stop_id}")["data"]


def get_eta(operator: str, stop_id: str, route: str, service_type: str):
    if operator in KMB_LIKE_OPERATORS:
        return fetch_json(f"{KMB_BASE}/eta/{stop_id}/{quote(route)}/{service_type}")["data"]
    return fetch_json(f"{CITYBUS_BASE}/eta/CTB/{stop_id}/{quote(route)}")["data"]


def normalize_text(s: str) -> str:
    cleaned = (s or "").strip().lower()
    for ch in "()[]{}.,，。／/\\-_:;：'\"":
        cleaned = cleaned.replace(ch, " ")
    return " ".join(cleaned.split())


def matches(stop_name: str, query: str) -> bool:
    stop = normalize_text(stop_name)
    q = normalize_text(query)
    if not q:
        return False
    if q in stop:
        return True
    return all(token in stop for token in q.split())


def minutes_until(eta_iso: str):
    eta_dt = datetime.fromisoformat(eta_iso)
    now = datetime.now(TZ)
    return max(0, round((eta_dt - now).total_seconds() / 60))


def build_eta_entry(row: dict):
    if not row.get("eta"):
        return None
    return {
        "eta": row["eta"],
        "minutes": minutes_until(row["eta"]),
        "destination_tc": row.get("dest_tc", ""),
        "destination_en": row.get("dest_en", ""),
        "remark_tc": row.get("rmk_tc", ""),
        "remark_en": row.get("rmk_en", ""),
    }


def format_match_line(match: dict) -> str:
    operator = match["operator"].upper()
    stop_name_tc = match.get("stop_name_tc") or match.get("stop_name_en") or match["stop_id"]
    dest = match.get("route_destination_tc") or match.get("route_destination_en") or ""
    suffix = f" → {dest}" if dest else ""
    return (
        f"- [{operator}] {stop_name_tc}{suffix} "
        f"[{match['direction']}, seq {match['sequence']}, stop {match['stop_id']}]"
    )


def main():
    p = argparse.ArgumentParser(description="Query Hong Kong bus ETA by route + stop keyword")
    p.add_argument("route", help="route number, e.g. 74X or 20")
    p.add_argument("stop_query", help="stop or area keyword, e.g. 九龍灣 / Kowloon Bay / 啟德")
    p.add_argument("--operator", choices=["kmb", "lwb", "citybus", "ctb"], default="kmb")
    p.add_argument("--direction", choices=["inbound", "outbound", "both"], default="both")
    p.add_argument("--service-type", default="1", help="KMB/LWB only; ignored for Citybus")
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    operator = normalize_operator(args.operator)
    directions = [args.direction] if args.direction != "both" else ["outbound", "inbound"]
    out = {
        "operator": operator,
        "route": args.route,
        "stop_query": args.stop_query,
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "matches": [],
    }

    for direction in directions:
        try:
            route_stops = get_route_stops(operator, args.route, normalize_direction(direction, operator), args.service_type)
        except Exception as e:
            out.setdefault("errors", []).append({"direction": direction, "error": str(e)})
            continue

        for rs in route_stops:
            stop = get_stop(operator, rs["stop"])
            if not any(
                matches(stop.get(name, ""), args.stop_query)
                for name in ["name_tc", "name_en", "name_sc"]
            ):
                continue

            eta_rows = get_eta(operator, rs["stop"], args.route, args.service_type)
            if operator in KMB_LIKE_OPERATORS:
                eta_rows = [
                    row for row in eta_rows
                    if row.get("dir") == rs.get("bound") and int(row.get("seq", -1)) == int(rs.get("seq", -1))
                ]
                route_destination_tc = ""
                route_destination_en = ""
            else:
                dir_code = "O" if direction == "outbound" else "I"
                eta_rows = [
                    row for row in eta_rows
                    if row.get("dir") == dir_code and int(row.get("seq", -1)) == int(rs.get("seq", -1))
                ]
                first = eta_rows[0] if eta_rows else {}
                route_destination_tc = first.get("dest_tc", "")
                route_destination_en = first.get("dest_en", "")

            etas = [entry for entry in (build_eta_entry(row) for row in eta_rows[: args.limit]) if entry]
            out["matches"].append(
                {
                    "operator": operator,
                    "direction": direction,
                    "sequence": int(rs["seq"]),
                    "service_type": rs.get("service_type", args.service_type),
                    "stop_id": rs["stop"],
                    "stop_name_tc": stop.get("name_tc", ""),
                    "stop_name_en": stop.get("name_en", ""),
                    "route_destination_tc": route_destination_tc,
                    "route_destination_en": route_destination_en,
                    "etas": etas,
                }
            )

    out["matches"].sort(key=lambda m: (m["direction"], m["sequence"]))

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    print(f"Operator {operator.upper()} | Route {out['route']} @ {out['generated_at']}")
    if not out["matches"]:
        print(f"No stop matched query: {args.stop_query}")
        if out.get("errors"):
            for err in out["errors"]:
                print(f"  {err['direction']}: {err['error']}")
        return

    for match in out["matches"]:
        print(format_match_line(match))
        if not match["etas"]:
            print("  No ETA available")
            continue
        for eta in match["etas"]:
            remark = f" ({eta['remark_tc']})" if eta["remark_tc"] else ""
            destination = eta["destination_tc"] or eta["destination_en"]
            print(f"  {eta['minutes']} 分鐘後 → {destination} @ {eta['eta']}{remark}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
