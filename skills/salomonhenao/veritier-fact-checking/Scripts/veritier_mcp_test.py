#!/usr/bin/env python3
"""
Veritier MCP Integration Test
==============================
Verifies that your Veritier MCP stdio proxy is correctly configured
and can communicate with the Veritier API.

Usage:
  1. Install dependencies:
     pip install mcp httpx anyio

  2. Set your API key:
     export VERITIER_API_KEY="vt_your_api_key_here"

  3. Place this file in the same directory as veritier_mcp_proxy.py

  4. Run the test:
     python veritier_mcp_test.py

Expected output:
  ✓ Initialize: server=veritier-proxy v1.0.0
  ✓ Tools discovered: ['verify_text']
  ✓ Verification result:
    Claim: 'The Eiffel Tower is located in Berlin.'
    Verdict: False
    Confidence: 1.0
    Explanation: The Eiffel Tower is located in Paris, France, not Berlin.
    Sources: https://...

More info: https://veritier.ai/docs#mcp
"""

import asyncio
import json
import os
import sys
from pathlib import Path


async def test_mcp_proxy():
    api_key = os.getenv("VERITIER_API_KEY", "")

    if not api_key:
        print("✗ Error: VERITIER_API_KEY environment variable is not set.")
        print("  Get your free API key at https://veritier.ai/register")
        sys.exit(1)

    # Locate the proxy script in the same directory as this test
    proxy_path = Path(__file__).parent / "veritier_mcp_proxy.py"
    if not proxy_path.exists():
        print(f"✗ Error: Cannot find veritier_mcp_proxy.py")
        print(f"  Expected at: {proxy_path}")
        print(f"  Download it from: https://veritier.ai/veritier_mcp_proxy.py")
        sys.exit(1)

    print(f"  Proxy: {proxy_path}")
    print(f"  Key:   {'*' * 8} (length: {len(api_key)})\n")

    # Launch the standalone proxy as a subprocess
    proc = await asyncio.create_subprocess_exec(
        sys.executable, str(proxy_path),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={**os.environ, "VERITIER_API_KEY": api_key},
    )

    async def send(msg: dict):
        proc.stdin.write((json.dumps(msg) + "\n").encode())
        await proc.stdin.drain()

    async def recv(timeout: int = 90) -> dict | None:
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=timeout)
        return json.loads(line.decode()) if line else None

    try:
        # Step 1: Initialize
        await send({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "veritier-mcp-test", "version": "1.0"}
            }
        })
        init = await recv(timeout=15)
        server_info = init["result"]["serverInfo"]
        print(f"✓ Initialize: server={server_info['name']} v{server_info['version']}")

        # Step 2: Send initialized notification
        await send({"jsonrpc": "2.0", "method": "notifications/initialized"})

        # Step 3: List tools
        await send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = await recv(timeout=10)
        tool_names = [t["name"] for t in tools["result"]["tools"]]
        print(f"✓ Tools discovered: {tool_names}")

        if "verify_text" not in tool_names:
            print("✗ Error: 'verify_text' tool not found.")
            sys.exit(1)

        # Step 4: Call verify_text with a known false claim
        test_claim = "The Eiffel Tower is located in Berlin."
        print(f"\n⏳ Verifying: \"{test_claim}\"")

        await send({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "verify_text", "arguments": {"text": test_claim}}
        })
        result = await recv(timeout=90)
        content = result["result"]["content"][0]["text"]

        print(f"✓ Verification result:\n")
        for line in content.split("\n"):
            print(f"  {line}")

        print("\n✓ All checks passed! Your MCP integration is working correctly.")

    except asyncio.TimeoutError:
        print("✗ Error: Timed out waiting for a response from the proxy.")
        print("  Make sure the 'mcp' package is installed: pip install mcp")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    finally:
        proc.stdin.close()
        await proc.wait()


if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Veritier MCP Integration Test")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    asyncio.run(test_mcp_proxy())
