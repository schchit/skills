# Advanced Topics

Expert patterns, optimization, and integration deep-dives.

---

## Multi-Agent Coordination via KV Store

### Pattern: Request-Response Queue

Agent A publishes a request, Agent B processes it, stores result.

```javascript
// Agent A: Request
await kv_set("workflow", `request_${Date.now()}`, JSON.stringify({
  type: "scrape_url",
  url: "https://example.com",
  timestamp: new Date().toISOString()
}));

// Agent B: Poll and process
async function processRequests() {
  const requests = await kv_list("workflow", prefix: "request_");
  
  for (const { key, value } of requests) {
    const request = JSON.parse(value);
    
    // Process
    const result = await scrapeUrl(request.url);
    
    // Store result with same key
    await kv_set("workflow", key.replace("request_", "result_"), JSON.stringify(result));
    
    // Mark processed
    await kv_delete("workflow", key);
  }
}
```

### Pattern: Checkpoint-Based Resumption

Large job can be resumed from last checkpoint.

```javascript
// Agent A: Scrape 1000 items with checkpoints
async function scrapeWithCheckpoints() {
  const lastCheckpoint = JSON.parse(await kv_get("pipeline", "checkpoint") || '{"index": 0}');
  const items = await fetchItemList();
  
  for (let i = lastCheckpoint.index; i < items.length; i++) {
    const item = items[i];
    const data = await scrapeItem(item);
    
    await kv_set("pipeline", `item_${i}`, JSON.stringify(data));
    
    // Save checkpoint every 100 items
    if (i % 100 === 0) {
      await kv_set("pipeline", "checkpoint", JSON.stringify({ index: i + 1 }));
    }
  }
  
  // Cleanup
  await kv_delete("pipeline", "checkpoint");
}
```

---

## Session Persistence & Auto-Reattach (v0.6.0+)

Chrome browser windows now survive daemon restarts. You no longer lose sessions when the daemon crashes or is intentionally restarted.

### How It Works

- **TCP-only Chrome transport** — Chrome runs on `--remote-debugging-port` on `127.0.0.1`, independent of the daemon process
- **Session registry** — daemon stores session metadata (profile, debug port, security params) in its DB
- **Startup reconciliation** — on every daemon/MCP startup, scans the registry and TCP-reattaches to surviving Chrome instances; dead sessions are cleaned up automatically
- **Graceful shutdown** — SIGTERM/SIGINT leaves Chrome alive; Chrome windows persist until the daemon restarts and reattaches

### Example: Daemon Restart Workflow

```javascript
// Start working
const sessionId = await open_session({ profile: "agent-work" });
const [tab] = await list_tabs(sessionId);
await navigate(sessionId, tab.target_id, "https://internal.mycompany.com");

// ... daemon crashes or is intentionally stopped ...

// After restart: sessions auto-reattach
// Same session_id works again — tabs, cookies, and scroll position preserved
const tabs = await list_tabs(sessionId);  // Same tabs, same state

// Or: list all surviving sessions
const allSessions = await list_sessions();  // Shows reattached sessions
```

### Practical Impact

| Before v0.6.0 | After v0.6.0 |
|---|---|
| Daemon restart = lost sessions | Daemon restart = Chrome survives, reattaches |
| Had to re-open and re-auth | Existing sessions resume automatically |
| Session IDs became stale | Same session IDs work after reattach |

---

## Auto-Checkpoints & Configurable Retention (v0.6.0+)

### Auto-Checkpoints

Pagerunner now automatically saves session state checkpoints:
- **On `close_session`** — always writes an "Autosave · close" checkpoint
- **Periodically** — every 5 minutes by default while sessions are active

This means you can restore state from the last checkpoint even if the session was closed without an explicit `save_snapshot`.

### Configuration

Add to `~/.pagerunner/config.toml`:

```toml
[checkpoints]
enabled = true
interval_seconds = 300  # How often to auto-checkpoint (default: 300 = 5 min)

[retention]
max_snapshot_versions = 10   # How many snapshot versions to keep (default: 10)
site_knowledge_ttl_days = 0  # Days before snapshots expire (default: 0 = indefinite)
```

**Key options:**
- `interval_seconds` — lower for more frequent checkpoints (e.g., `60` for every minute), `0` to disable periodic checkpoints
- `max_snapshot_versions` — controls disk usage; older versions are pruned when limit is hit
- `site_knowledge_ttl_days = 0` — indefinite retention (default); set to `30` to expire after 30 days

---

## Daemon Mode & Multi-Client Coordination

### Setup

```bash
# Start daemon once (persistent, always-on)
pagerunner daemon &

# All `pagerunner mcp` instances auto-detect daemon
# No manual coordination needed

# Graceful shutdown — Chrome windows survive
kill $(pgrep -f "pagerunner daemon")

# Restart — daemon auto-reattaches to Chrome windows
pagerunner daemon &
```

### Verification

```bash
# See daemon process
ps aux | grep pagerunner

# Daemon logs
tail -f ~/.pagerunner/daemon.log

# Multiple MCP clients share state
pagerunner list-sessions  # Sees all active sessions across all clients
```

---

## Performance Optimization

### Batch Operations

Instead of sequential waits:

```javascript
// ❌ SLOW — wait after each action
for (const url of urls) {
  await navigate(sessionId, tabId, url);
  await wait_for(sessionId, tabId, selector: ".content", ms: 5000);
  const content = await get_content(sessionId, tabId);
}

// ✅ FAST — parallelize where possible
const promises = urls.map(async url => {
  const s = await open_session({ profile: "scraper" });
  const [tab] = await list_tabs(s);
  await navigate(s, tab.target_id, url);
  await wait_for(s, tab.target_id, selector: ".content");
  const content = await get_content(s, tab.target_id);
  await close_session(s);
  return content;
});

const results = await Promise.all(promises);
```

### Efficient Selectors

```javascript
// ❌ SLOW — traverses entire DOM
const count = document.querySelectorAll('div').filter(el => el.textContent.includes('Item')).length;

// ✅ FAST — targeted query
const count = document.querySelectorAll('[data-testid="item"]').length;
```

### Caching Results

```javascript
// ❌ SLOW — re-evaluate every time
const count1 = await evaluate(..., "document.querySelectorAll('.item').length");
const count2 = await evaluate(..., "document.querySelectorAll('.item').length");

// ✅ FAST — evaluate once, cache
const count = await evaluate(..., "document.querySelectorAll('.item').length");
// Use cached value multiple times
```

---

## Security Patterns (Beyond SECURITY.md)

### Role-Based Access

Different agent profiles for different roles:

```toml
[[profiles]]
name = "agent-readonly"
# Limited to read-only operations
user_data_dir = "/path/to/readonly/profile"

[[profiles]]
name = "agent-write"
# Can fill forms, submit
user_data_dir = "/path/to/write/profile"
```

### Token Rotation

Periodically refresh snapshots:

```javascript
// Every 24 hours
setInterval(async () => {
  const sessionId = await open_session({ profile: "agent-work" });
  const [tab] = await list_tabs(sessionId);
  
  await navigate(sessionId, tab.target_id, "https://app.example.com");
  // Force re-auth if session expired
  await evaluate(sessionId, tab.target_id, "document.querySelector('.logout-btn')?.click()");
  
  // Re-login
  await fill(sessionId, tab.target_id, "input[type='email']", agentEmail);
  // ... complete login ...
  
  // Update snapshot
  await save_snapshot(sessionId, tab.target_id, origin: "https://app.example.com");
  await close_session(sessionId);
}, 24 * 60 * 60 * 1000);
```

---

## Debugging Advanced Workflows

### Performance Profiling

```javascript
// Measure each operation
const start = Date.now();

await navigate(...);
console.log(`navigate: ${Date.now() - start}ms`);

await wait_for(...);
console.log(`wait_for: ${Date.now() - start}ms`);

await get_content(...);
console.log(`get_content: ${Date.now() - start}ms`);
```

### State Inspection

```javascript
// Inspect internal state at any point
const state = await evaluate(sessionId, tabId, `
  ({
    url: window.location.href,
    title: document.title,
    memoryUsage: performance.memory?.usedJSHeapSize || 'N/A',
    sessionState: window.__STORE__.getState()
  })
`);

console.log("Current state:", state);
```

---

## Integration with External Services

### API Calls with Auth

```javascript
// Use browser context to make authenticated API calls
const response = await evaluate(sessionId, tabId, `
  fetch('https://api.example.com/data', {
    headers: {
      'Authorization': 'Bearer ' + window.__AUTH_TOKEN__
    }
  }).then(r => r.json())
`);
```

### Database Operations

```javascript
// After scraping, insert into database
const scrapedData = await get_content(sessionId, tabId);

await fetch('https://internal-api.company.com/data', {
  method: 'POST',
  body: JSON.stringify({ data: scrapedData }),
  headers: { 'Authorization': `Bearer ${process.env.API_KEY}` }
});
```

---

## Troubleshooting Advanced Issues

### Memory Leaks

If daemon memory grows over time:

```bash
# Check daemon memory
ps aux | grep pagerunner | grep -v grep

# Restart daemon to free memory
pkill -f "pagerunner daemon"
pagerunner daemon &
```

### Stale Sessions

Sessions should be closed after use. In v0.6.0+, `close_session` also writes an auto-checkpoint, so closing cleanly is even more valuable:

```javascript
// ❌ WRONG — session never closed (no auto-checkpoint written)
const sessionId = await open_session(...);
// ... do work ...
// forgot to close_session

// ✅ RIGHT — always close; triggers auto-checkpoint on close
try {
  const sessionId = await open_session(...);
  // ... do work ...
} finally {
  await close_session(sessionId);  // Writes "Autosave · close" checkpoint
}
```

---

## Best Practices Checklist

- [ ] Use daemon mode for multi-agent workflows
- [ ] Store credentials in KV, not code
- [ ] Close sessions when done (use try/finally) — triggers auto-checkpoint
- [ ] Cache results when possible
- [ ] Monitor daemon logs for errors
- [ ] Use specific selectors (not DOM traversal)
- [ ] Parallelize independent operations
- [ ] Checkpoint long-running jobs
- [ ] Test with sample data first
- [ ] Enable audit logging for security-sensitive workflows
- [ ] Tune `[checkpoints] interval_seconds` for your workflow (lower = more resilient, more disk)
- [ ] Set `[retention] max_snapshot_versions` to prevent unbounded disk growth

---

## Next Steps

- Implement KV-based coordination for your multi-agent pipeline
- Profile performance bottlenecks
- Set up daemon for always-on automation
- Integrate with external APIs and databases

See EXAMPLES.md for multi-agent patterns in action.
