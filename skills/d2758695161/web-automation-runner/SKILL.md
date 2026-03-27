# web-automation-runner

Run browser automation tasks on any website using Playwright. Scraping, form filling, data extraction, screenshots — all through natural language instructions.

## Usage

```
Scrape [what] from [URL]
Extract [data description] from [URL]
Fill and submit [form details] on [URL]
Take a screenshot of [URL]
Monitor [element/text] on [URL] and alert when it changes
```

## What It Does

The agent uses a real Chromium browser to:
- Navigate to any URL
- Click buttons, fill forms, select dropdowns
- Wait for elements or text to appear
- Extract structured data from pages
- Take screenshots (viewport or full page)
- Handle dialogs (alerts, confirmations, prompts)
- Run custom JavaScript on the page

## Examples

- "Scrape all job listings from remoteok.com - need title, company, salary, and apply link"
- "Fill out the contact form on example.com/contact using: name=John, email=john@mail.com, message=Hi"
- "Take a screenshot of this dashboard and save it to dashboard.png"
- "Extract all product names and prices from amazon.com/s?k=laptop"
- "Login to [site] with username X and password Y, then scrape my order history"

## Data Formats

Extracted data is returned as structured text or written to files:
- CSV for tabular data
- JSON for structured records
- TXT for plain text

## Limitations

- Cannot bypass CAPTCHAs or login barriers (except credentials you provide)
- Rate-limited sites may need delays
- Heavy pages may take longer to load
- No PDF generation from dynamic content

## Notes

- Uses Playwright with Chromium (headless)
- All actions are logged with timestamps
- Screenshots saved to workspace with descriptive names
