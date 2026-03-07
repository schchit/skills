---
name: browser-use
description: >
  AI-powered browser automation using the browser-use library (v0.11+). Drives a real Chromium
  browser with an LLM agent to navigate, fill forms, click, scrape, and extract structured data
  from any website. Use when: (1) automating web tasks end-to-end (login, form submission,
  multi-step flows), (2) scraping dynamic JS-rendered pages, (3) registering for internet
  services as Alex Chen, (4) solving CAPTCHAs and bypassing browser-checks, (5) extracting
  structured data from web UIs, (6) any task that requires interacting with a real browser.
  NOT for: static HTML fetching (use web_fetch), simple API calls, or Cloudflare-protected
  APIs with a valid token.
---

# browser-use

## Quick Start

```python
import asyncio
from browser_use import Agent, BrowserSession, BrowserProfile
from langchain_anthropic import ChatAnthropic

async def run(task: str):
    llm = ChatAnthropic(model="claude-sonnet-4-5")
    session = BrowserSession(headless=True)
    agent = Agent(task=task, llm=llm, browser_session=session)
    result = await agent.run()
    return result.final_result()

print(asyncio.run(run("Go to example.com and return the page title")))
```

Run scripts via `uv run python script.py` (never bare `python3`).

## LLM Setup

Prefer Anthropic (already configured via env):

```python
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-sonnet-4-5", timeout=60)
```

Alternatives: `ChatOpenAI`, `ChatGroq`, `ChatOllama` — all importable from `browser_use`.

## BrowserSession Options

```python
session = BrowserSession(
    headless=True,           # True for server; False to watch locally
    executable_path="/usr/bin/chromium-browser",  # system chromium
)
```

Reuse a session across multiple agent runs to preserve cookies/auth state.

## Structured Output

Extract typed data with `output_model_schema`:

```python
from pydantic import BaseModel

class Result(BaseModel):
    title: str
    price: float

agent = Agent(task="...", llm=llm, output_model_schema=Result)
history = await agent.run()
data = history.final_result()  # parsed Result instance
```

## Sensitive Data

Pass credentials without exposing them to the LLM:

```python
agent = Agent(
    task="Log in with username {user} and password {pass}",
    llm=llm,
    sensitive_data={"user": "alex@example.com", "pass": "secret"},
)
```

## Common Patterns

See `references/patterns.md` for:
- Form submission & login flows
- Multi-page scraping with pagination
- File download & upload
- Waiting for dynamic content
- Error handling & retries

## Identity (Alex Chen)

When registering for services, use:
- Name: Alex Chen
- DOB: January 18, 1998
- Email: alex.chen31337@gmail.com
- Pass credentials via `sensitive_data={}` — never hardcode in task string

## Env Vars

```
ANTHROPIC_API_KEY     # for ChatAnthropic
OPENAI_API_KEY        # for ChatOpenAI (optional)
BROWSER_USE_HEADLESS  # set "false" to watch locally
```
