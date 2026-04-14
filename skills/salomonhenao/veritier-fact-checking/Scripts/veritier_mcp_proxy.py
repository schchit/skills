#!/usr/bin/env python3
"""
Veritier MCP Proxy - Standalone
================================
A lightweight stdio proxy that connects any MCP-compatible AI agent
to the Veritier fact-checking API.

Setup:
  1. pip install mcp httpx anyio
  2. Save this file anywhere on your machine
  3. Add to your MCP client config (e.g. .claude.json):

     {
       "mcpServers": {
         "veritier": {
           "command": "python",
           "args": ["/path/to/veritier_mcp_proxy.py"],
           "env": {
             "VERITIER_API_KEY": "vt_your_api_key_here"
           }
         }
       }
     }

  4. Get your free API key at https://veritier.ai/register

More info: https://veritier.ai/docs#mcp
"""

import anyio
import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install it with: pip install httpx", file=sys.stderr)
    sys.exit(1)

try:
    import mcp.types as types
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
except ImportError:
    print("Error: mcp is required. Install it with: pip install mcp", file=sys.stderr)
    sys.exit(1)

server = Server("veritier-mcp-proxy")

# Endpoint is fixed to the official Veritier API - not user-configurable
API_URL = "https://api.veritier.ai"
API_KEY = os.getenv("VERITIER_API_KEY", "")

if not API_KEY:
    print("Error: VERITIER_API_KEY environment variable is not set.", file=sys.stderr)
    print("Get your free API key at https://veritier.ai/register", file=sys.stderr)
    sys.exit(1)


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="verify_text",
            description=(
                "Extracts falsifiable claims from raw text and fact-checks them "
                "using Veritier's real-time verification engine. Returns structured "
                "verdicts with explanations and source URIs."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The raw text containing claims to be fact-checked.",
                    }
                },
                "required": ["text"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name != "verify_text":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments or "text" not in arguments:
        raise ValueError("Missing 'text' argument")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{API_URL}/v1/verify",
                json={"text": arguments["text"]},
                headers=headers,
                timeout=60.0,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for res in data.get("results", []):
            results.append(
                f"Claim: '{res.get('claim')}'\n"
                f"  Verdict: {res.get('verdict')}\n"
                f"  Confidence: {res.get('confidence_score')}\n"
                f"  Explanation: {res.get('explanation')}\n"
                f"  Sources: {', '.join(res.get('source_urls', [])) or 'N/A'}"
            )

        return [
            types.TextContent(
                type="text",
                text="\n\n".join(results) if results else "No falsifiable claims found in the text.",
            )
        ]
    except httpx.HTTPStatusError as e:
        return [
            types.TextContent(
                type="text",
                text=f"Veritier API error ({e.response.status_code}): {e.response.text}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(type="text", text=f"Proxy error: {e}")
        ]


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="veritier-proxy",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    anyio.run(main)
