#!/usr/bin/env python3
"""Secure Tailscale network manager.

Whitelisted commands only. Blocks destructive/unauthorized operations.
Masks public IPs in output.

Usage:
    tailscale_ctrl.py status          # Network status
    tailscale_ctrl.py devices         # Connected devices
    tailscale_ctrl.py ip              # Tailscale IPs
    tailscale_ctrl.py ping <host>     # Ping a tailnet device
    tailscale_ctrl.py netcheck        # Network diagnostics
    tailscale_ctrl.py serve-status    # Current serve/funnel config
    tailscale_ctrl.py whois <ip>      # Who is this IP
"""

import argparse
import json
import re
import subprocess
import sys

# Only these subcommands are allowed
READ_COMMANDS = {"status", "ip", "ping", "netcheck", "whois", "serve-status"}
# Write commands require explicit flag
WRITE_COMMANDS = {"serve", "unserve"}

# IP patterns to mask (public IPv4 and IPv6)
PUBLIC_IP_RE = re.compile(
    r'\b(?!(100\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|127\.|::1|fe80:))'
    r'(?:\d{1,3}\.){3}\d{1,3}\b'
)


def mask_public_ips(text: str) -> str:
    """Replace public IPs (v4 and v6) with [IP-MASKED]."""
    text = PUBLIC_IP_RE.sub("[IP-MASKED]", text)
    # Simple IPv6 mask: full addresses that aren't link-local or Tailscale (fd7a:)
    text = re.sub(
        r'(?<![0-9a-fA-F:])(?!(?:fd7a|fe80|::1))(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}',
        '[IP-MASKED]', text
    )
    return text


def run_tailscale(args: list[str], timeout: int = 15) -> dict:
    """Execute a tailscale command safely."""
    cmd = ["tailscale"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = mask_public_ips(result.stdout)
        error = mask_public_ips(result.stderr)
        return {
            "returncode": result.returncode,
            "stdout": output.strip(),
            "stderr": error.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out ({timeout}s)"}
    except FileNotFoundError:
        return {"error": "tailscale not found in PATH"}
    except Exception as e:
        return {"error": str(e)}


def get_status():
    """Get tailnet status."""
    return run_tailscale(["status"])


def get_status_json():
    """Get detailed status as JSON."""
    result = run_tailscale(["status", "--json"])
    if "error" in result:
        return result
    try:
        data = json.loads(result["stdout"])
        # Extract key info, hide sensitive details
        summary = {
            "self": {
                "name": data.get("Self", {}).get("DNSName", "?"),
                "online": data.get("Self", {}).get("Online", False),
                "tailscale_ips": data.get("Self", {}).get("TailscaleIPs", []),
            },
            "peers": [],
        }
        for peer_id, peer in data.get("Peer", {}).items():
            summary["peers"].append({
                "name": peer.get("DNSName", peer.get("HostName", "?")),
                "online": peer.get("Online", False),
                "ips": peer.get("TailscaleIPs", []),
                "os": peer.get("OS", "?"),
                "last_seen": peer.get("LastSeen", "?"),
            })
        return summary
    except json.JSONDecodeError:
        return {"raw": result["stdout"]}


def get_devices():
    """List connected devices."""
    status = get_status_json()
    if "peers" in status:
        return status
    return status


def get_ip():
    """Get Tailscale IPs."""
    return run_tailscale(["ip"])


def ping_host(host: str):
    """Ping a tailnet host."""
    return run_tailscale(["ping", "-c", "3", host], timeout=20)


def netcheck():
    """Run network diagnostics."""
    return run_tailscale(["netcheck"], timeout=30)


def serve_status():
    """Show current serve config."""
    return run_tailscale(["serve", "status"])


def whois(ip_or_name: str):
    """Look up who an IP/name belongs to."""
    return run_tailscale(["whois", ip_or_name])


def format_output(data):
    """Format for human-readable output."""
    if isinstance(data, dict):
        if "error" in data:
            return f"❌ {data['error']}"
        if "stdout" in data:
            return data["stdout"] or data.get("stderr", "(empty)")
        if "self" in data:
            lines = []
            s = data["self"]
            lines.append(f"📍 This device: {s['name']} ({'online' if s['online'] else 'offline'})")
            lines.append(f"   IPs: {', '.join(s.get('tailscale_ips', []))}")
            if data.get("peers"):
                lines.append(f"\n👥 Peers ({len(data['peers'])}):")
                for p in data["peers"]:
                    status = "🟢" if p["online"] else "🔴"
                    lines.append(f"  {status} {p['name']} ({p.get('os', '?')}) — {', '.join(p.get('ips', []))}")
            return "\n".join(lines)
        return json.dumps(data, indent=2)
    return str(data)


def main():
    parser = argparse.ArgumentParser(description="Secure Tailscale manager")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status")
    sub.add_parser("devices")
    sub.add_parser("ip")
    sub.add_parser("netcheck")
    sub.add_parser("serve-status")

    p_ping = sub.add_parser("ping")
    p_ping.add_argument("host")

    p_whois = sub.add_parser("whois")
    p_whois.add_argument("target")

    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "status":
        data = get_status_json() if args.json else get_status()
    elif args.command == "devices":
        data = get_devices()
    elif args.command == "ip":
        data = get_ip()
    elif args.command == "ping":
        data = ping_host(args.host)
    elif args.command == "netcheck":
        data = netcheck()
    elif args.command == "serve-status":
        data = serve_status()
    elif args.command == "whois":
        data = whois(args.target)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(data, indent=2, default=str))
    else:
        print(format_output(data))


if __name__ == "__main__":
    main()
