---
name: gemini-citation
description: Conduct evidence-based research with exact, accurate APA citations using the Gemini API's 'scientific citation' (Google Search grounding) feature. Use when Xiaoyan (Research Assistant) or others need highly factual, cited research summaries, literature reviews, or exact evidence with inline APA citations tied to real web sources.
---

# Gemini Citation

## Overview

This skill leverages the Gemini API's Google Search Grounding feature to return heavily factual, exact evidence directly tied to search results, along with properly formatted APA inline and trailing citations. It guarantees that generated facts are grounded in live web references rather than model hallucinations.

## Quick Start

You can use the provided script to query the Gemini API with search grounding enabled.

### 1. Requirements

Ensure the `GEMINI_API_KEY` is set in your environment and the `google-genai` package is installed:

```bash
export GEMINI_API_KEY="your-api-key"
pip install google-genai
```

### 2. Running a Research Query

Execute the `gemini_cite.py` script with your research topic. The script automatically forces the Gemini API to use Google Search Grounding and requests strict APA formatting.

```bash
python scripts/gemini_cite.py "Recent breakthroughs in solid-state battery technology"
```

To see structured JSON output containing the exact source titles and URIs used by the model:

```bash
python scripts/gemini_cite.py "Recent breakthroughs in solid-state battery technology" --format json
```

## How It Works

1. **Google Search Grounding:** The API call is configured with `tools=[{"google_search": {}}]`. This forces the model to fetch live information before generating a response.
2. **Strict APA Instructions:** The script's prompt injects an explicit requirement to use "Author, Year" inline citations and to list all references in proper APA format at the end.
3. **Grounding Metadata Verification:** The script extracts the `grounding_chunks` from the Gemini API response metadata and displays the exact source URLs and titles that the model used, ensuring that you have an auditable list of sources alongside the generated APA citations.

## When to Use

- **Literature Reviews:** When Xiaoyan is tasked with gathering current state-of-the-art information on a technical or scientific topic.
- **Fact-Checking:** When you need exact evidence and verifiable URLs rather than general knowledge.
- **Academic Writing:** When strict APA formatting and inline citations are a requirement for the final output.

## Resources

### scripts/

- `gemini_cite.py`: A Python CLI tool that handles the Gemini API call, enables Google Search grounding, enforces APA citations, and parses the grounding metadata to output verifiable source links.

## Advanced Usage

If you prefer to write your own API scripts, the core pattern for enabling exact citations with `google-genai` is:

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model='gemini-2.5-pro',
    contents='Your research query here...',
    config=types.GenerateContentConfig(
        tools=[{"google_search": {}}]
    )
)

# Access sources
for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
    print(chunk.web.title, chunk.web.uri)
```
