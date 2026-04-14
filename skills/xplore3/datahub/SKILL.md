---
name: datahub
description: >
  Call any data interface through natural language with DataHub API.
  Supports async querying, result polling, API supply addition, and data bounties.
  Use when: User needs real-time data, wants to add new API supplies, or initiate data bounties.
  NOT for: Local file operations, simple Q&A without external data needs.
version: 1.1.0
author: DataHub Team
tags:
  - api
  - data
  - query
  - async
  - bounty
  - api-supply
triggers:
  - "query.*data"
  - "get.*information"
  - "fetch.*"
  - "add.*api"
  - "supply.*api"
  - "bounty.*data"
  - "reward.*data"
---

# DataHub Skill

Call any data interface through natural language. Submit queries, add API supplies, or create data bounties - all through the same simple interface with automatic polling for results.

## Core Capabilities

1. **Natural Language Queries**: Convert user's natural language into API calls
2. **Async Result Polling**: Automatically poll until data is ready
3. **API Supply Addition**: Add new API supplies using natural language + documentation link
4. **Data Bounties**: Initiate data bounties when requested data is unavailable
5. **Response Parsing**: Handle both JSON and Markdown formatted responses

## When to Use

- User needs real-time data (weather, news, exchange rates, etc.)
- User wants to add a new API supply to the system
- User cannot find desired data and wants to offer a bounty
- Need to call external APIs for structured data

## When NOT to Use

- Local file read/write operations
- Pure computation tasks (no external data needed)
- Scenarios requiring sub-second real-time responses

## Prerequisites: Getting an API Key

Before using this Skill, you need a DataHub API Key. Two ways to get one:

### Option 1: Apply via Website

1. Visit DataHub official website: https://seekin.chat
2. Register or log in to your account
3. Navigate to "API Management" or "Developer" page
4. Create a new API Key and copy it

### Option 2: Get it Directly in Chat

1. Visit https://seekin.chat
2. Simply type in the website's chat dialog:
  - Please give me an API Key
  - I want to apply for an API key

3. The system will automatically generate and return an API Key

> 💡 **Tip**: New users typically receive free credits sufficient for daily use.

### Configuring the API Key

After obtaining your API Key, configure it using one of these methods:

**Method A: Environment Variable (Recommended)**
```bash
export DATAHUB_API_KEY="your-api-key-here"
Method B: User Config File
Create ~/.datahub/config.json:

json
{
  "apiKey": "your-api-key-here"
}
Method C: Project Config File
Create datahub.config.json in your project root:

json
{
  "apiKey": "your-api-key-here"
}
Configuration priority: Environment Variable > User Config > Project Config

Workflows
Workflow 1: Standard Data Query
Use this when the user simply wants to fetch data.

Step 1: Submit Query
Execute scripts/query.js to submit the user's natural language query:

bash
node scripts/query.js "<user's natural language query>" [sessionId]
Parameters:

First argument: User's natural language query (required)

Second argument: Session ID for context retention (optional)

Response Format:

json
{
  "success": true,
  "processId": "xxx-xxx-xxx",
  "message": "Query submitted"
}

Step 2: Poll for Results
Execute scripts/poll.js to poll for the processed result:

bash
node scripts/poll.js <processId> [--max-attempts 60] [--interval 1000]
Parameters:

processId: Process ID returned from Step 1 (required)

--max-attempts: Maximum polling attempts, default 60

--interval: Polling interval in milliseconds, default 1000

Response Format:

json
{
  "success": true,
  "data": { ... },
  "attempts": 5,
  "elapsed": 5234
}

Step 3: Parse and Present Results
If JSON returned, present key information in a structured way

If Markdown text returned, maintain original formatting

If query fails, explain possible reasons and provide suggestions

Workflow 2: Adding an API Supply
Use this when the user wants to add a new API supply to the system. The user provides a natural language description and a documentation link.

Step 1: Submit API Supply Addition
Execute scripts/query.js with a specially formatted query that includes the API documentation link:

bash
node scripts/query.js "Add API supply: <description>. Documentation: <DocLink>" [sessionId]
Example:

bash
node scripts/query.js "Add API supply: Weather API that returns current conditions and forecast. Documentation: https://weather-api.example.com/docs"
Alternative Natural Language Formats:

"I want to add a new API for stock data. Docs: https://stock-api.example.com"

"Supply a translation API. DocLink: https://translate-api.example.com/docs"

"Register new data source for cryptocurrency prices: https://crypto-api.example.com"

Step 2: Poll for Confirmation
Execute scripts/poll.js with the returned processId:

bash
node scripts/poll.js <processId>
Expected Response:

json
{
  "success": true,
  "data": {
    "apiId": "new-api-xxx",
    "status": "registered",
    "message": "API supply successfully added and pending approval"
  }
}
Step 3: Confirm to User
Inform the user that:

The API supply has been submitted

It will be reviewed and activated shortly

They can start using it once approved

Workflow 3: Creating a Data Bounty
Use this when the user requests data that is not currently available, and they want to offer a reward/bounty for it.

Step 1: Submit Data Bounty
Execute scripts/query.js with a query describing the desired data and bounty details:

bash
node scripts/query.js "Create data bounty: <data description>. Reward: <bounty details>" [sessionId]
Examples:

bash
# Simple bounty
node scripts/query.js "Create data bounty: I need historical weather data for Tokyo from 2020-2023. Reward: $50"

# Detailed bounty
node scripts/query.js "Bounty: Looking for real-time satellite imagery API for agriculture monitoring. Will pay $200 for working API supply"

# Natural language
node scripts/query.js "I can't find data on global coffee prices. I'll offer a $30 bounty for anyone who can supply this data"
Alternative Natural Language Formats:

"I need data on X but can't find it. Can I create a bounty?"

"Offer reward for Y dataset"

"Start a bounty for Z API. Reward: $100"

"The data I want isn't available. How can I request it with a bounty?"

Step 2: Poll for Bounty Creation Confirmation
Execute scripts/poll.js with the returned processId:

bash
node scripts/poll.js <processId>
Expected Response:

json
{
  "success": true,
  "data": {
    "bountyId": "bounty-xxx-xxx",
    "status": "active",
    "description": "Historical weather data for Tokyo 2020-2023",
    "reward": "$50",
    "createdAt": "2024-01-15T10:30:00Z",
    "message": "Bounty created successfully"
  }
}
Step 3: Inform User
Provide the user with:

Bounty ID for tracking

Confirmation that the bounty is now active

Estimated timeframe (if available)

How they can check bounty status later

Usage Examples
Example 1: Weather Query
User Input: "What's the weather like in Beijing today?"

Execution:

bash
# 1. Submit query
RESULT=$(node scripts/query.js "What's the weather like in Beijing today?")
PROCESS_ID=$(echo $RESULT | jq -r '.processId')

# 2. Poll for result
node scripts/poll.js $PROCESS_ID
Expected Output: Structured weather data

Example 2: News Query
User Input: "Latest tech news"

Execution: Same workflow as above

Example 3: Contextual Conversation with Session
User Input 1: "My name is John"

bash
node scripts/query.js "My name is John" "session-001"
User Input 2: "What did I say my name was?"

bash
node scripts/query.js "What did I say my name was?" "session-001"
Example 4: Adding an API Supply
User Input: "I want to add a new API for currency exchange rates. Here's the documentation: https://exchangerate-api.com/docs"

Execution:

bash
# 1. Submit API supply
RESULT=$(node scripts/query.js "Add API supply: Currency exchange rates API with daily updates. Documentation: https://exchangerate-api.com/docs")
PROCESS_ID=$(echo $RESULT | jq -r '.processId')

# 2. Poll for confirmation
node scripts/poll.js $PROCESS_ID
Example 5: Creating a Data Bounty
User Input: "I can't find any API for real-time air quality in my city. I'd like to offer a $75 bounty for someone to provide this data."

Execution:

bash
# 1. Submit bounty
RESULT=$(node scripts/query.js "Create data bounty: Real-time air quality data API for major cities. Reward: $75")
PROCESS_ID=$(echo $RESULT | jq -r '.processId')

# 2. Poll for confirmation
node scripts/poll.js $PROCESS_ID
