#!/usr/bin/env python3
"""Run a browser-use Agent from the command line.

Usage:
    uv run python skills/browser-use/scripts/run_agent.py "Go to example.com and return the title"
    uv run python skills/browser-use/scripts/run_agent.py "..." --model claude-sonnet-4-5 --headless
"""
import argparse
import asyncio
import json
import os
import sys


async def main(task: str, model: str, headless: bool, output_json: bool):
    from browser_use import Agent, BrowserSession
    from langchain_anthropic import ChatAnthropic

    llm = ChatAnthropic(model=model, timeout=60)
    session = BrowserSession(
        headless=headless,
        executable_path=os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium-browser"),
    )

    agent = Agent(task=task, llm=llm, browser_session=session, max_failures=3)
    history = await agent.run()
    result = history.final_result()

    if output_json:
        print(json.dumps({"result": result, "steps": len(history.history)}))
    else:
        print(result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run browser-use agent")
    parser.add_argument("task", help="Task for the agent to perform")
    parser.add_argument("--model", default="claude-sonnet-4-5", help="LLM model")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    parser.add_argument("--json", dest="output_json", action="store_true")
    args = parser.parse_args()

    asyncio.run(main(args.task, args.model, args.headless, args.output_json))
