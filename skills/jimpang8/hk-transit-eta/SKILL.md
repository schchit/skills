---
name: hk-bus-eta
description: Query Hong Kong bus ETA and stop data for route + place questions using official KMB/LWB and Citybus open-data endpoints. Use when the user asks in Cantonese, Chinese, or English things like「74X 幾多分鐘後喺九龍灣有車」「A41 去機場而家幾時到青衣站」「城巴 20 喺啟德幾耐到」「幫我查某條線經唔經某個站／地區」or any message that combines a bus route with a stop name, landmark, estate, station, area, destination, direction, or ETA intent.
---

# HK Bus ETA

Use the bundled script to answer Hong Kong bus route + stop/place questions quickly and consistently.

## Quick start

Run:

```bash
python3 /home/jim/.openclaw/workspace/skills/hk-bus-eta/scripts/hk_bus_eta.py <route> <stop-keyword>
```

Examples:

```bash
python3 /home/jim/.openclaw/workspace/skills/hk-bus-eta/scripts/hk_bus_eta.py 74X 九龍灣
python3 /home/jim/.openclaw/workspace/skills/hk-bus-eta/scripts/hk_bus_eta.py A41 青衣 --operator lwb
python3 /home/jim/.openclaw/workspace/skills/hk-bus-eta/scripts/hk_bus_eta.py 20 啟德 --operator citybus
python3 /home/jim/.openclaw/workspace/skills/hk-bus-eta/scripts/hk_bus_eta.py 20 "Kai Tak" --operator citybus --direction outbound
python3 /home/jim/.openclaw/workspace/skills/hk-bus-eta/scripts/hk_bus_eta.py 74X 九龍灣 --direction outbound
python3 /home/jim/.openclaw/workspace/skills/hk-bus-eta/scripts/hk_bus_eta.py 74X 九龍灣 --json
```

## Extraction workflow

1. Extract the route first.
   - Examples: `74X`, `A41`, `20`, `NA31`.
2. Extract the stop or area keyword next.
   - Accept stop names, stations, estates, landmarks, districts, malls, piers, airports, hospitals, or short area names.
   - Treat messages like `74X 九龍灣幾耐到`, `A41 青衣站有冇車`, `城巴20啟德幾時到` as route + place queries.
3. Infer operator if the user says it explicitly.
   - `九巴` → `--operator kmb`
   - `龍運` / `Long Win` → `--operator lwb`
   - `城巴` / `Citybus` → `--operator citybus`
   - If the user does not say, default to KMB. If the route obviously looks like a Citybus-only route or the first attempt fails, retry with `--operator citybus`.
4. If the user hints at direction or destination, pass it through.
   - `去機場`, `往尖沙咀`, `outbound`, `返去` often imply direction disambiguation.
   - Use `--direction outbound` or `--direction inbound` when the user's wording clearly prefers one side.
5. Run the script with the route and keyword.
6. If multiple stop matches appear, summarize each clearly with operator, direction, stop name, sequence, and destination.
7. Report ETA in natural language, usually in minutes first.
8. If no match appears, say so and ask for a more specific stop name, estate, station, or direction.

## Operator notes

- `kmb`: KMB routes via official `data.etabus.gov.hk` KMB endpoints.
- `lwb`: Long Win is handled through the same KMB-family endpoint structure used by airport and North Lantau routes in the KMB dataset.
- `citybus`: Citybus routes via official `rt.data.gov.hk/v2/transport/citybus` endpoints.

## Matching behavior

- Stop matching is flexible substring/token matching against Traditional Chinese, Simplified Chinese, and English stop names.
- Short area names often work even when the actual stop includes extra qualifiers like road names, schools, or bus-stop codes.
- If the user gives only a broad area, try that first, then refine using the returned candidates.

## Reporting guidance

- Prefer a concise answer like `74X 喺九龍灣下一班大約 3 分鐘後到。`
- If there are multiple likely matches, list them instead of guessing.
- If there is no ETA, say that clearly rather than implying no service.
- Use `--json` only when structured output is easier for follow-up processing.

## Scope and limitations

- This skill currently supports KMB, Long Win, and Citybus only.
- NWFB is not separate here; use Citybus data where applicable under the current official dataset.
- The script does not yet auto-detect the operator with certainty from route number alone; explicit operator hints from the user are more reliable.
- Broad place names can still match multiple stops, so disambiguation may be needed.

## scripts/

- `scripts/hk_bus_eta.py` — query KMB/LWB or Citybus route stops, resolve stop keywords, and fetch ETA for matched stop(s).
