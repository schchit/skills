# Deployment Guide - image-upscale-mcp

## Prerequisites

1. Apify account with API token
2. Node.js 20+
3. Docker installed (for local testing)

## Environment Variables

Set these in the Apify actor configuration:

```bash
NTRIQ_AI_URL=https://ai.ntriq.co.kr  # AI server (optional, default already set)
```

## Local Testing

```bash
# Install dependencies
npm install

# Run locally (MCP mode)
npm start

# Expected output:
# [info] Starting Image Upscale MCP Server...
# [info] MCP Server connected and ready to receive requests
```

## Build & Deploy to Apify

```bash
# 1. Log in to Apify CLI
apify auth --token YOUR_APIFY_TOKEN

# 2. Validate configuration
docker compose config --quiet  # if using docker-compose
npm run lint                    # optional: add linter to scripts

# 3. Push to Apify
apify push

# 4. Tag as latest
apify push --tag latest

# 5. Get your actor ID from Apify dashboard
# Example: yourname-image-upscale-mcp
```

## Verify Deployment

```bash
# Test on Apify platform
apify call YOUR_ACTOR_ID --wait

# Expected: Actor runs and charges correctly
```

## Pricing & Monetization

### Pay-Per-Event Configuration
The actor is configured as a **paid actor**:
- **upscale_image**: $0.08 per execution
- **enhance_face**: $0.10 per execution

### Revenue Split
- Apify: 20%
- Developer: 80%

### Charge() Implementation
✅ Both tools call `await Apify.Actor.charge()` after successful execution
✅ Charges are recorded in the `pay_per_event.json` file
✅ Events are saved to the actor's dataset

## Monitoring

After deployment, monitor via Apify Dashboard:

1. **Runs**: Check individual execution logs
2. **Dataset**: View stored results with timestamps
3. **Billing**: Track charges per event type
4. **Metrics**: Response time, error rate

## Troubleshooting

### "charge() method not found"
- Ensure `apify` package version ≥ 3.1.0 in package.json
- Update: `npm install apify@^3.1.0`

### "Cannot reach ai.ntriq.co.kr"
- Verify network connectivity
- Check NTRIQ_AI_URL environment variable
- Fallback to default: `https://ai.ntriq.co.kr`

### Timeout Issues
- Default timeout: 195 seconds (180s processing + 15s buffer)
- For larger images, timeout may be too short
- Adjust TIMEOUT_MS in src/handlers/upscale.js if needed

### MCP Not Responding
- Check StdioServerTransport is connected
- Verify MCP SDK version in package.json
- Review logs in Apify dashboard

## Maintenance

### Update AI Server URL
```bash
# Change in Apify actor settings or code
NTRIQ_AI_URL=https://new-ai-server.com
```

### Update Pricing
1. Modify `CHARGE_MAP` in src/main.js
2. Update `pay_per_event.json` prices
3. Redeploy: `apify push`

### Monitor Real-ESRGAN Uptime
- Check ai.ntriq.co.kr health endpoint regularly
- Set up alerts in monitoring system

## Next Steps

1. Deploy to Apify: `apify push`
2. Configure pricing via Apify Dashboard
3. Add to RapidAPI for global exposure
4. Monitor performance & refine timeout settings
