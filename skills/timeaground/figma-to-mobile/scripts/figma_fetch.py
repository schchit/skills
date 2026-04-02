#!/usr/bin/env python3
"""Fetch and simplify Figma node data for mobile code generation."""

import json
import os
import re
import sys

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)


def parse_figma_url(url: str):
    """Extract file_key and node_id from a Figma URL."""
    file_match = re.search(r"figma\.com/(?:file|design)/([a-zA-Z0-9]+)", url)
    node_match = re.search(r"node-id=([0-9]+[-:][0-9]+)", url)
    if not file_match:
        return None, None
    file_key = file_match.group(1)
    node_id = node_match.group(1).replace("-", ":") if node_match else None
    return file_key, node_id


def rgba_to_hex(color: dict) -> str:
    """Convert Figma RGBA (0-1) to hex #RRGGBB or #AARRGGBB."""
    r = round(color.get("r", 0) * 255)
    g = round(color.get("g", 0) * 255)
    b = round(color.get("b", 0) * 255)
    a = round(color.get("a", 1) * 255)
    if a == 255:
        return f"#{r:02X}{g:02X}{b:02X}"
    return f"#{a:02X}{r:02X}{g:02X}{b:02X}"

def extract_effects(node: dict) -> list:
    """Extract shadow and blur effects from a node."""
    effects = node.get("effects", [])
    result = []
    for effect in effects:
        if not effect.get("visible", True):
            continue
        etype = effect.get("type")
        if etype in ("DROP_SHADOW", "INNER_SHADOW"):
            shadow = {"type": etype.lower().replace("_", "-")}
            color = effect.get("color")
            if color:
                shadow["color"] = rgba_to_hex(color)
            offset = effect.get("offset", {})
            shadow["offsetX"] = offset.get("x", 0)
            shadow["offsetY"] = offset.get("y", 0)
            shadow["radius"] = effect.get("radius", 0)
            shadow["spread"] = effect.get("spread", 0)
            result.append(shadow)
        elif etype == "LAYER_BLUR":
            result.append({"type": "blur", "radius": effect.get("radius", 0)})
    return result


def extract_fills(fills: list) -> dict:
    """Extract fill info: solid color, image, or gradient."""
    result = {}
    for fill in fills:
        if not fill.get("visible", True):
            continue
        ftype = fill.get("type")
        if ftype == "SOLID":
            result["backgroundColor"] = rgba_to_hex(fill.get("color", {}))
            break
        elif ftype == "IMAGE":
            result["hasImage"] = True
            break
        elif ftype in ("GRADIENT_LINEAR", "GRADIENT_RADIAL", "GRADIENT_ANGULAR", "GRADIENT_DIAMOND"):
            grad = {"type": ftype}
            stops = fill.get("gradientStops", [])
            if stops:
                grad["stops"] = [
                    {"color": rgba_to_hex(s.get("color", {})), "position": round(s.get("position", 0), 3)}
                    for s in stops
                ]
            result["gradient"] = grad
            break
    return result

def simplify_node(node: dict, parent_pos: dict = None) -> dict:
    """Simplify a Figma node to only the info needed for code generation."""
    bbox = node.get("absoluteBoundingBox", {})
    node_type = node.get("type")
    result = {
        "id": node.get("id"),
        "type": node_type,
        "name": node.get("name"),
        "width": bbox.get("width"),
        "height": bbox.get("height"),
    }

    # Component instance detection
    if node_type == "INSTANCE":
        comp_id = node.get("componentId")
        if comp_id:
            result["componentId"] = comp_id

    # Relative position
    if parent_pos and bbox:
        result["x"] = round(bbox.get("x", 0) - parent_pos.get("x", 0), 1)
        result["y"] = round(bbox.get("y", 0) - parent_pos.get("y", 0), 1)

    # Fills (background color, image, or gradient)
    fills = node.get("fills", [])
    fill_info = extract_fills(fills)
    result.update(fill_info)

    # Effects (shadows, blur)
    effects = extract_effects(node)
    if effects:
        result["effects"] = effects

    # Border / strokes
    strokes = node.get("strokes", [])
    for stroke in strokes:
        if stroke.get("type") == "SOLID" and stroke.get("visible", True):
            result["borderColor"] = rgba_to_hex(stroke.get("color", {}))
            result["borderWidth"] = node.get("strokeWeight", 1)
            break

    # Corner radius (uniform or per-corner)
    cr = node.get("cornerRadius")
    if cr and cr > 0:
        result["cornerRadius"] = cr
    else:
        radii = node.get("rectangleCornerRadii")
        if radii and any(r > 0 for r in radii):
            result["cornerRadii"] = radii  # [topLeft, topRight, bottomRight, bottomLeft]

    # Text properties
    if node_type == "TEXT":
        result["text"] = node.get("characters", "")
        style = node.get("style", {})
        if style:
            result["fontSize"] = style.get("fontSize")
            result["fontWeight"] = style.get("fontWeight")
            result["fontFamily"] = style.get("fontFamily")
            result["textAlignHorizontal"] = style.get("textAlignHorizontal")
            result["lineHeightPx"] = style.get("lineHeightPx")
            result["letterSpacing"] = style.get("letterSpacing")
        # Text color from fills
        for fill in fills:
            if fill.get("type") == "SOLID" and fill.get("visible", True):
                result["textColor"] = rgba_to_hex(fill.get("color", {}))
                break

    # Auto-layout
    layout_mode = node.get("layoutMode")
    if layout_mode:
        result["layoutMode"] = layout_mode
        result["itemSpacing"] = node.get("itemSpacing", 0)
        result["paddingLeft"] = node.get("paddingLeft", 0)
        result["paddingRight"] = node.get("paddingRight", 0)
        result["paddingTop"] = node.get("paddingTop", 0)
        result["paddingBottom"] = node.get("paddingBottom", 0)
        paa = node.get("primaryAxisAlignItems")
        if paa:
            result["primaryAxisAlignItems"] = paa
        caa = node.get("counterAxisAlignItems")
        if caa:
            result["counterAxisAlignItems"] = caa
        pss = node.get("primaryAxisSizingMode")
        if pss:
            result["primaryAxisSizingMode"] = pss
        css = node.get("counterAxisSizingMode")
        if css:
            result["counterAxisSizingMode"] = css
        lg = node.get("layoutGrow")
        if lg:
            result["layoutGrow"] = lg

    # Opacity
    opacity = node.get("opacity")
    if opacity is not None and opacity < 1:
        result["opacity"] = round(opacity, 3)

    # Visibility
    if not node.get("visible", True):
        result["visible"] = False

    # Children
    children = node.get("children", [])
    if children:
        current_pos = {"x": bbox.get("x", 0), "y": bbox.get("y", 0)}
        result["children"] = [
            simplify_node(child, current_pos)
            for child in children
            if child.get("visible", True)
        ]

    return result

def has_truncated_children(node: dict) -> bool:
    """Check if any node looks like it should have children but doesn't.
    Heuristic: FRAME/GROUP/INSTANCE/COMPONENT with no children but non-trivial size."""
    ntype = node.get("type")
    children = node.get("children", [])
    if ntype in ("FRAME", "GROUP", "INSTANCE", "COMPONENT", "COMPONENT_SET") and not children:
        bbox = node.get("absoluteBoundingBox", {})
        w = bbox.get("width", 0)
        h = bbox.get("height", 0)
        if w > 10 and h > 10:
            return True
    for child in children:
        if has_truncated_children(child):
            return True
    return False


def fetch_node(file_key: str, node_id: str, token: str, depth: int = 5) -> dict:
    """Fetch a node from Figma API with adaptive depth."""
    api_node_id = node_id.replace(":", "-")
    url = f"https://api.figma.com/v1/files/{file_key}/nodes?ids={api_node_id}&depth={depth}"
    headers = {"X-Figma-Token": token}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if "err" in data:
        raise Exception(f"Figma API error: {data['err']}")

    node_data = data.get("nodes", {}).get(node_id)
    if not node_data:
        raise Exception(f"Node {node_id} not found in response")

    document = node_data["document"]

    # Adaptive depth: if children seem truncated, retry with deeper depth
    if depth < 15 and has_truncated_children(document):
        new_depth = min(depth + 5, 15)
        print(f"Depth {depth} may be insufficient, retrying with depth={new_depth}...", file=sys.stderr)
        return fetch_node(file_key, node_id, token, new_depth)

    return document


def export_svgs(file_key: str, node_ids: list, token: str) -> dict:
    """Export nodes as SVG via Figma API. Returns {node_id: svg_string}."""
    ids_param = ",".join(node_ids)
    url = f"https://api.figma.com/v1/images/{file_key}?ids={ids_param}&format=svg"
    headers = {"X-Figma-Token": token}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = {}
    images = data.get("images", {})
    for nid, svg_url in images.items():
        if svg_url:
            try:
                svg_resp = requests.get(svg_url, timeout=30)
                svg_resp.raise_for_status()
                results[nid] = svg_resp.text
            except Exception as e:
                print(f"Warning: failed to download SVG for {nid}: {e}", file=sys.stderr)
                results[nid] = None
        else:
            results[nid] = None
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python figma_fetch.py <figma_url> [--depth N] [--export-svg id1,id2,...]")
        print("Example: python figma_fetch.py 'https://www.figma.com/design/ABC/Project?node-id=100-200'")
        print("Export:  python figma_fetch.py 'https://...?node-id=...' --export-svg 24249:6824,24249:6827")
        sys.exit(1)

    url = sys.argv[1]
    depth = 5
    export_ids = None

    if "--depth" in sys.argv:
        idx = sys.argv.index("--depth")
        depth = int(sys.argv[idx + 1])

    if "--export-svg" in sys.argv:
        idx = sys.argv.index("--export-svg")
        export_ids = sys.argv[idx + 1].split(",")

    token = os.environ.get("FIGMA_TOKEN")

    # Try .env file in working directory if env var not set
    if not token:
        for env_path in [".env", "../.env"]:
            if os.path.exists(env_path):
                with open(env_path) as ef:
                    for line in ef:
                        line = line.strip()
                        if line.startswith("FIGMA_TOKEN="):
                            token = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
            if token:
                break

    if not token:
        print("FIGMA_TOKEN_NOT_SET")
        print("")
        print("To configure: ask the user for their Figma Personal Access Token,")
        print("then write it to the project root .env file:")
        print("")
        print("  echo 'FIGMA_TOKEN=figd_xxx' >> .env")
        print("")
        print("The token starts with 'figd_'. The user can get one at:")
        print("  Figma > avatar (top-left) > Settings > Security > Personal Access Tokens")
        sys.exit(1)

    file_key, node_id = parse_figma_url(url)
    if not file_key:
        print(f"ERROR: Could not parse Figma URL: {url}")
        sys.exit(1)

    # SVG export mode
    if export_ids:
        print(f"Exporting {len(export_ids)} node(s) as SVG...", file=sys.stderr)
        svgs = export_svgs(file_key, export_ids, token)
        print(json.dumps(svgs, indent=2, ensure_ascii=False))
        return

    # Normal fetch mode
    if not node_id:
        print("ERROR: URL must contain a node-id parameter.")
        print("Open a specific frame in Figma and copy the URL.")
        sys.exit(1)

    print(f"Fetching node {node_id} from file {file_key} (depth={depth})...", file=sys.stderr)
    raw_node = fetch_node(file_key, node_id, token, depth)
    simplified = simplify_node(raw_node)

    output_json = json.dumps(simplified, indent=2, ensure_ascii=False)
    # Check for --output flag
    output_file = None
    for i, a in enumerate(sys.argv):
        if a == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"Written to {output_file}", file=sys.stderr)
    else:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        print(output_json)


if __name__ == "__main__":
    main()
