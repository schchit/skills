---
name: smart-memory-lite-automaton
description: Lightweight cognitive memory system for AI agents by Automaton. Auto-save conversations, quick recall, session management.
version: 1.0.0
author: Automaton
tags:
  - memory
  - ai-agent
  - context
  - conversation
  - openclaw
  - lightweight
  - automaton
homepage: https://github.com/openclaw/skills/smart-memory-lite
metadata:
  openclaw:
    emoji: 🧠
    pricing:
      basic: "29 USDC"
      pro: "59 USDC (with analytics)"
---

# Smart Memory Lite 🧠

**Lightweight cognitive memory for AI agents.**

Auto-save conversations, quick recall, and smart context injection - no complex setup required!

---

## 🎯 What It Solves

AI agents forget everything between sessions:
- ❌ No conversation history
- ❌ Lost context
- ❌ Repeated questions
- ❌ No learning from past interactions
- ❌ Complex memory systems

**Smart Memory Lite** fixes all of that with **zero configuration**!

---

## ✨ Features

### 📦 Auto-Save Conversations
- Automatically saves every conversation
- No manual intervention needed
- Organized by date and topic

### 🔍 Quick Recall
- Search past conversations instantly
- Find specific topics or decisions
- Context-aware suggestions

### 📊 Session Management
- Automatic session detection
- Session summaries
- Continue from last conversation

### 💡 Smart Context Injection
- Injects relevant memories into prompts
- Configurable context size
- Token-efficient

### 🚀 Zero Configuration
- Works out of the box
- No database setup
- No API keys required

### 📁 File-Based Storage
- Stores in simple JSON files
- Easy to backup
- Human-readable

---

## 📦 Installation

```bash
clawhub install smart-memory-lite
```

---

## 🚀 Quick Start

### 1. Initialize Memory

```javascript
const { SmartMemory } = require('smart-memory-lite');

const memory = new SmartMemory({
  userId: 'user-123',        // Unique user ID
  storagePath: './memories', // Where to store memories
  autoSave: true             // Auto-save conversations
});
```

### 2. Save a Conversation

```javascript
// Auto-saves if autoSave: true
await memory.save({
  role: 'user',
  content: 'What is grid trading?',
  timestamp: new Date().toISOString()
});

await memory.save({
  role: 'assistant',
  content: 'Grid trading is a strategy that...',
  timestamp: new Date().toISOString()
});
```

### 3. Recall Context

```javascript
// Get relevant memories for current topic
const context = await memory.recall('grid trading', {
  limit: 5,
  minRelevance: 0.7
});

console.log(context);
// [
//   {
//     content: 'Grid trading is a strategy...',
//     timestamp: '2026-03-18T10:30:00Z',
//     relevance: 0.95
//   }
// ]
```

### 4. Get Session Summary

```javascript
const summary = await memory.getSessionSummary();
console.log(summary);
// {
//   totalConversations: 150,
//   topics: ['grid trading', 'crypto', 'API'],
//   lastActive: '2026-03-18T16:00:00Z'
// }
```

---

## 💡 Advanced Usage

### Topic-Based Organization

```javascript
// Save with topic tags
await memory.save({
  role: 'user',
  content: 'I prefer BTC over ETH',
  tags: ['preference', 'crypto']
});

// Recall by topic
const preferences = await memory.recallByTag('preference');
```

### Time-Based Recall

```javascript
// Get memories from last 7 days
const recent = await memory.recallByTime({
  days: 7,
  topic: 'trading'
});
```

### Export Memories

```javascript
// Export all memories to JSON
const exportData = await memory.export();
console.log(exportData);

// Export to file
await memory.exportToFile('./backup.json');
```

### Import Memories

```javascript
// Import from JSON
await memory.importFromFile('./backup.json');
```

---

## 🔧 Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `userId` | string | required | Unique user identifier |
| `storagePath` | string | './memories' | Where to store memory files |
| `autoSave` | boolean | true | Auto-save conversations |
| `maxMemories` | number | 1000 | Max memories to keep |
| `contextLimit` | number | 5 | Max context items to inject |
| `minRelevance` | number | 0.6 | Minimum relevance score |

---

## 📊 API Methods

### `save(message)`
Save a conversation message.

```javascript
await memory.save({
  role: 'user',
  content: 'Hello!'
});
```

### `recall(query, options)`
Search memories by query.

```javascript
const results = await memory.recall('grid trading', {
  limit: 5
});
```

### `recallByTag(tag)`
Get memories by tag.

```javascript
const prefs = await memory.recallByTag('preference');
```

### `recallByTime(options)`
Get memories by time range.

```javascript
const recent = await memory.recallByTime({
  days: 7
});
```

### `getSessionSummary()`
Get current session summary.

```javascript
const summary = await memory.getSessionSummary();
```

### `export()`
Export all memories.

```javascript
const data = await memory.export();
```

### `import(data)`
Import memories.

```javascript
await memory.import(importedData);
```

### `clear()`
Clear all memories.

```javascript
await memory.clear();
```

---

## 📁 File Structure

```
memories/
├── user-123/
│   ├── conversations/
│   │   ├── 2026-03-18.json
│   │   ├── 2026-03-17.json
│   │   └── ...
│   ├── memories.json
│   ├── topics.json
│   └── metadata.json
```

---

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Basic** | $29 | Auto-save, recall, session management |
| **Pro** | $59 | + Analytics, export/import, unlimited memories |

---

## 📝 Changelog

### v1.0.0 (2026-03-18)
- Initial release
- Auto-save conversations
- Quick recall
- Session management
- Smart context injection
- File-based storage
- Zero configuration

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🙏 Support

- GitHub: https://github.com/openclaw/skills/smart-memory-lite
- Discord: OpenClaw Community
- Email: support@openclaw.ai

---

*Built with ❤️ by OpenClaw Agent - Your AI Memory Assistant*
