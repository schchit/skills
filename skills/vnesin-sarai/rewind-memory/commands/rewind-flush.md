# /rewind-flush

Flush the KG extraction queue to Modal (Pro tier only).

## Usage

```
/rewind-flush
```

## Instructions

When the user runs `/rewind-flush`:

1. Check the queue size:
   ```bash
   python3 -c "
   import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/hooks')
   from batch_queue import queue_size
   print(f'{queue_size()} items pending')
   "
   ```

2. If items are pending, flush them:
   ```bash
   python3 -c "
   import sys, json; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/hooks')
   from batch_queue import flush_queue
   from rewind_bridge import get_config
   cfg = get_config()
   url = cfg.get('modal', {}).get('extract_batch_url', '')
   token = cfg.get('modal', {}).get('auth_token', '')
   if not url: print('Not configured — set modal.extract_batch_url in rewind config')
   else: print(json.dumps(flush_queue(url, token), indent=2))
   "
   ```

3. Show results: how many texts were processed, nodes/edges extracted.

Note: The queue automatically flushes on session end. This command is for manual mid-session flushes.
