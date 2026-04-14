# /rewind-setup

Initialise Rewind Memory for this workspace.

## What this command does

Run `/rewind-setup` to detect the best available configuration and write
`~/.rewind/config.yaml` automatically.

---

## Instructions for Claude Code

When the user runs `/rewind-setup`, execute the following steps **in order**:

### Step 1 — Check for an existing config

```bash
test -f ~/.rewind/config.yaml && echo "EXISTS" || echo "MISSING"
```

If the file **already exists**, show its contents and ask the user whether to
reconfigure. If they say no, stop here.

### Step 2 — Detect Ollama

```bash
curl -sf http://localhost:11434/api/tags > /dev/null && echo "OLLAMA_UP" || echo "OLLAMA_DOWN"
```

### Step 3a — Ollama available → Free tier with graph KG

Pull the graph extraction model and write a free-tier config:

```bash
ollama pull saraidefence/graph-preflexor:latest
```

Write `~/.rewind/config.yaml`:

```yaml
tier: free
embedding:
  provider: local
  model: all-MiniLM-L6-v2
  dim: 768
kg:
  provider: ollama
  model: saraidefence/graph-preflexor:latest
  base_url: http://localhost:11434
data_dir: ~/.rewind/data
```

### Step 3b — No Ollama → Free tier with heuristic KG

Write `~/.rewind/config.yaml`:

```yaml
tier: free
embedding:
  provider: local
  model: all-MiniLM-L6-v2
  dim: 768
kg:
  provider: heuristic
  # Regex-based entity extraction. No LLM required.
data_dir: ~/.rewind/data
```

### Step 4 — Initialise data directory

```bash
rewind init
```

If `rewind` is not installed, install it first:

```bash
pip install rewind-memory
```

### Step 5 — Health check

```bash
rewind health
```

Parse the output and report back to the user:

- Which layers are active
- Embedding provider in use
- KG provider in use
- Data directory location

### Step 6 — Pro upgrade prompt

If the user does **not** already have `modal.auth_token` set in their config,
show this message:

> **Want cloud-powered memory?**
> Upgrade to Rewind Pro ($9/mo) for NV-Embed-v2 4096-dim embeddings, Graph-PReFLexOR knowledge extraction, and cross-encoder reranking — all running on Modal cloud.
> Run: `rewind upgrade` or visit https://rewind.sh/pro

---

## Notes

- Never overwrite an existing config without explicit user confirmation.
- The `heuristic` provider works offline with no model downloads.
- The `ollama` KG provider requires ~4 GB of VRAM for the preflexor model.
