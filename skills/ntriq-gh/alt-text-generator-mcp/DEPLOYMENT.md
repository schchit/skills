# Deployment Guide - Alt Text Generator MCP

## Pre-Deployment Checklist

- [ ] All files present (package.json, Dockerfile, src/*, .actor/*)
- [ ] Dependencies correct (@modelcontextprotocol/sdk ^1.10.0, apify ^3.1.0, etc.)
- [ ] Actor.charge() implemented with await
- [ ] Disclaimer in README.md
- [ ] Disclaimer in all API responses
- [ ] pay_per_event.json eventNames match CHARGE_MAP in code
- [ ] MCP tools registered (generate_alt_text, generate_detailed_description)

## Local Testing

```bash
# Install dependencies
npm install

# Run locally
npm start
# Server runs on http://localhost:3000

# Health check
curl http://localhost:3000/health

# Test generate_alt_text tool
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "generate_alt_text",
      "arguments": {
        "image_url": "https://example.com/test-image.jpg",
        "language": "en"
      }
    }
  }'
```

## Apify Deployment

### Step 1: Push to Apify

```bash
# From the actor directory
cd /Users/youareplan/Documents/Projects/apify-actors/alt-text-generator-mcp

# Authenticate with Apify
apify login

# Build and push
apify push
```

The push command will:
- Build Docker image
- Push code and schemas (.actor/ files)
- Validate all required schemas

### Step 2: Configure via Apify Console (if needed)

These settings CAN be done via console but are already configured:

1. **Categories**: MCP_SERVERS, AI, DEVELOPER_TOOLS
2. **Pricing Model**: Pay-Per-Event (already configured in pay_per_event.json)
3. **Standby Mode**: Enabled (usesStandbyMode: true in actor.json)

### Step 3: Test Cloud Execution

```bash
# Call the actor on Apify platform
apify call <actor-id>

# Use standby mode (always-on)
curl -X POST "https://ntriqpro--alt-text-generator-mcp.apify.actor/mcp?token=$APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "generate_alt_text",
      "arguments": {
        "image_url": "https://example.com/image.jpg",
        "language": "en"
      }
    }
  }'
```

## Important Notes

### Actor.charge() Behavior

The charging happens AFTER successful tool execution:

1. Tool handler executes
2. Result returned
3. If `status: "success"`, call `await Actor.charge({eventName, count: 1})`
4. If `status: "error"`, NO charge (automatic)

### Pricing in pay_per_event.json

Must match CHARGE_MAP in src/main.js:

```javascript
// src/main.js
const CHARGE_MAP = {
  generate_alt_text: 0.05,           // matches pay_per_event.json
  generate_detailed_description: 0.08 // matches pay_per_event.json
};
```

### API Endpoint Configuration

Ensure environment variable is set when needed:

```bash
# Production endpoint (set in Apify or .env)
AI_API_ENDPOINT=https://ai.ntriq.co.kr/analyze/image
AI_REQUEST_TIMEOUT=30000
```

### Disclaimer Requirement

Every API response MUST include disclaimer field:

```json
{
  "status": "success",
  "alt_text": "...",
  "disclaimer": "AI-generated. Not guaranteed WCAG/ADA compliant. Human review required.",
  ...
}
```

## Troubleshooting

### Docker Build Fails

```bash
# Clean and rebuild
docker system prune -a
apify build
```

### Connection to AI Service Fails

1. Check endpoint: `https://ai.ntriq.co.kr/analyze/image`
2. Verify timeout: 30000ms (30 seconds)
3. Check request format:
   ```json
   {
     "image_url": "https://...",
     "prompt": "...",
     "language": "en",
     "max_tokens": 150
   }
   ```

### MCP Endpoint Not Responding

1. Verify POST /mcp endpoint is registered
2. Check Express middleware order
3. Ensure McpServer is initialized before listening

## Performance Tuning

### Concurrency

Default: 1 request at a time (Express default)

To increase (if Apify container allows):

```bash
# In actor.json
"concurrency": 4  # Allows 4 parallel requests
```

### Timeouts

- AI Service timeout: 30 seconds (configurable)
- HTTP timeout: 30 seconds per request
- Apify execution timeout: 600 seconds (10 minutes) default

## Monitoring

### Logging

Structured logs are sent to stdout:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "info",
  "tool": "generate_alt_text",
  "message": "Success",
  "processing_time_ms": 1234,
  "alt_text_length": 125
}
```

### Apify Monitoring

1. View actor logs in Apify Console
2. Monitor runs tab for execution metrics
3. Check dataset for output records

## RapidAPI Integration (Optional)

If exposing via RapidAPI:

```bash
# Environment variables needed
RAPIDAPI_PROXY_SECRET=your-secret
```

Route configuration in rapidapi-wrapper:

```
POST /api/ai/alt-text → alt-text-generator-mcp:3000/mcp
```

## Next Steps

1. Push to Apify: `apify push`
2. Test in standby mode with actual images
3. Monitor logs for errors
4. Consider RapidAPI gateway integration for public API
