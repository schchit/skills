# browser-use Patterns

## Login Flow

```python
async def login_and_scrape(url, username, password):
    session = BrowserSession(headless=True)
    llm = ChatAnthropic(model="claude-sonnet-4-5")
    
    # Step 1: Login
    login_agent = Agent(
        task=f"Go to {url}/login and log in with username {{user}} and password {{pass}}",
        llm=llm,
        browser_session=session,
        sensitive_data={"user": username, "pass": password},
    )
    await login_agent.run()
    
    # Step 2: Reuse session (cookies preserved)
    scrape_agent = Agent(
        task="Navigate to the dashboard and extract all account details",
        llm=llm,
        browser_session=session,
    )
    return await scrape_agent.run()
```

## Multi-page Scraping with Pagination

```python
agent = Agent(
    task="""
    Go to https://example.com/listings.
    Extract all item names and prices from the current page.
    Click 'Next' and repeat until there is no next button.
    Return all items as a JSON list.
    """,
    llm=llm,
    max_actions_per_step=20,
)
result = await agent.run(max_steps=50)
```

## Structured Data Extraction

```python
from pydantic import BaseModel
from typing import list

class Product(BaseModel):
    name: str
    price: float
    url: str

class ProductList(BaseModel):
    products: list[Product]

agent = Agent(
    task="Go to https://store.example.com and extract all products on the first page",
    llm=llm,
    output_model_schema=ProductList,
)
history = await agent.run()
products = history.final_result()  # ProductList instance
```

## File Download

```python
import tempfile

async def download_file(url: str, download_url: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmpdir:
        session = BrowserSession(headless=True)
        agent = Agent(
            task=f"Go to {url}, find and click the download button, save the file",
            llm=llm,
            browser_session=session,
            file_system_path=tmpdir,
        )
        await agent.run()
        # Check tmpdir for downloaded files
```

## Form Registration (Service Signup)

```python
agent = Agent(
    task="""
    Go to {signup_url} and create an account:
    - Name: Alex Chen
    - Email: {email}
    - Password: {password}
    - Date of birth: January 18, 1998
    Complete any email verification if required.
    """,
    llm=llm,
    sensitive_data={
        "email": "alex.chen31337@gmail.com",
        "password": "<actual_password>",
    },
    max_failures=3,
)
```

## Error Handling & Retries

```python
from browser_use.exceptions import AgentError

async def safe_run(task: str, max_retries: int = 2):
    for attempt in range(max_retries + 1):
        try:
            session = BrowserSession(headless=True)
            agent = Agent(task=task, llm=llm, browser_session=session, max_failures=3)
            history = await agent.run()
            if history.is_done():
                return history.final_result()
        except Exception as e:
            if attempt == max_retries:
                raise
            await asyncio.sleep(2 ** attempt)
    return None
```

## Using system Chromium (no install needed)

```python
session = BrowserSession(
    headless=True,
    executable_path="/usr/bin/chromium-browser",
)
```

## Save Agent History / Screenshots

```python
agent = Agent(
    task="...",
    llm=llm,
    save_conversation_path="/tmp/agent_run/",
    generate_gif=True,  # saves a gif of the run
)
```
