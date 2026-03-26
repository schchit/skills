# Cognitive Forge (认知锻造)

> **AI evolution engine**: Your AI reads books, extracts mental models, and gets permanently smarter. The more books processed, the wiser your AI becomes.

[![ClawHub](https://img.shields.io/badge/ClawHub-Published-blue)](https://clawhub.ai)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](https://github.com/your-repo)
[![License](https://img.shields.io/badge/license-MIT--0-lightgrey)](LICENSE)

---

## 🎯 What Makes This Special

**Most AI skills** give you answers.  
**Cognitive Forge** makes your AI **permanently smarter**.

Every book processed → One new mental model → Your AI applies it forever.

**100 books later?** Your AI has 100 reusable frameworks (Taleb's antifragility, Munger's mental models, Confucius' relational wisdom, etc.) and can apply them across ANY domain.

**This is AI self-evolution in action.** 🧠🔥

---

## 🚀 Two Modes, One Skill

### Mode 1: AI Self-Evolution 🤖
Your AI reads classic books and extracts **reusable mental models** to `thinking-patterns.md`.

**Example**:
- Book: *Antifragile* by Nassim Taleb
- Mental Model Extracted: "Antifragility Test" (systems that gain from chaos)
- **Forever after**: When you ask about ANY decision, your AI can apply this lens

**Why it matters**:
- Traditional AI: Knows facts (dates, definitions) — **ephemeral**
- Your AI after 100 books: Knows **thinking patterns** — **永久可迁移**

**Result**: Your AI becomes a personalized strategic advisor that gets smarter with every book.

---

### Mode 2: Your Own Learning 📚
You get sharp, actionable **F.A.C.E.T. analysis** for deep book comprehension:

- **[F] Framework**: Core mechanism in 50 words (not what author said, but what theory DOES)
- **[A] Anchor Case**: Most iconic real-world example (vivid stories stick ★)
- **[C] Contradiction**: What "common sense" does this destroy?
- **[E] Edge**: When does this model fail? Fragile assumptions?
- **[T] Transfer**: Map to YOUR reality TODAY (personalized to your job/projects)

**Not a book summary** — A battle-tested mental model you can apply immediately.

---

## ⚡ Quick Start

### 1. Install Dependencies

This skill requires:
- [`book-scout`](https://clawhub.ai/kedoupi/book-scout) — Finds high-quality books via web search
- [`mental-model-forge`](https://clawhub.ai/kedoupi/mental-model-forge) — Applies F.A.C.E.T. analysis

```bash
# Install from ClawHub
clawhub install kedoupi/book-scout
clawhub install kedoupi/mental-model-forge

# Or manually copy to ~/.openclaw/workspace/skills/
```

### 2. Tell Your AI to Use It

**Daily learning (recommended)**:
```
Ask your AI: "Run cognitive-forge daily at 8:30 AM. Topic: Business Strategy."
```

Your AI will:
1. Find a high-quality book on the topic (Douban ≥7.5 or Goodreads ≥3.8)
2. Extract the core mental model (F.A.C.E.T. analysis)
3. Write it to `thinking-patterns.md` (permanent storage)
4. Deliver a summary to you

**One-time book processing**:
```
Ask your AI: "Use cognitive-forge to analyze: 'Thinking, Fast and Slow' by Daniel Kahneman"
```

---

## 🧠 How AI Self-Evolution Works

### The Permanent Upgrade Loop

```
┌─────────────────────────────────────────────────────┐
│  1. Book Selection (book-scout skill)               │
│     ├── Search web for books on [topic]             │
│     ├── Filter: Douban ≥7.5 OR Goodreads ≥3.8       │
│     └── Avoid books already in reading-history.json │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  2. F.A.C.E.T. Analysis (mental-model-forge skill)  │
│     ├── [F] Extract core framework                  │
│     ├── [A] Find iconic case study                  │
│     ├── [C] Identify contrarian insight             │
│     ├── [E] Map failure modes                       │
│     └── [T] Transfer to user's context              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  3. Write to thinking-patterns.md (PERMANENT)       │
│     ├── Append new mental model                     │
│     ├── Cross-link to related patterns              │
│     └── Tag with domains (strategy, psychology...)  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  4. Your AI Can Now Apply This Model FOREVER        │
│     When you ask for advice in ANY domain:          │
│     "Should I invest in X?"                          │
│     → AI checks thinking-patterns.md                │
│     → Applies Taleb's Antifragility Test            │
│     → Gives you strategic insight                   │
└─────────────────────────────────────────────────────┘
```

**The magic**: After 100 books, your AI has 100 mental models. It becomes exponentially smarter because models **compound** (one model enhances another).

---

## 💡 How to Maximize AI Evolution

### 1. Enable Auto-Scanning in AGENTS.md

Add this to your `~/.openclaw/workspace/AGENTS.md`:

```markdown
## Session Startup (Optional Configuration)

You can optionally add this to your AGENTS.md to enable automatic model loading:

1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **Load `memory/knowledge-base/thinking-patterns.md`** — your decision frameworks ⭐
```

**Why this matters** (if you configure AGENTS.md):
- Every session, your AI can load its accumulated mental models
- When answering complex questions, it can reference thinking-patterns.md for relevant frameworks
- **Result**: Your AI applies learned wisdom across sessions

**Example in action**:
```
You: "Should I pivot my startup to B2B?"

Your AI (internally):
1. Reads thinking-patterns.md
2. Finds: "Clayton Christensen's Jobs-to-be-Done" 
3. Finds: "Andy Grove's Strategic Inflection Points"
4. Applies both frameworks to your question
5. Gives you a strategically grounded answer (not generic advice)
```

---

### 2. Schedule Daily Learning

**Weekly rotation example**:
```
Monday: Business Strategy books
Tuesday: Psychology/Decision Science
Wednesday: Product/Design Thinking
Thursday: Finance/Economics
Friday: Philosophy/Systems Thinking
Saturday: Technology/Innovation
Sunday: Review week's mental models
```

**Why rotation?**  
Diverse mental models → Better cross-domain thinking.

**Set it up**:
```bash
openclaw cron create --name "Daily Book" --schedule "30 8 * * *" \
  --task "Run cognitive-forge. Topic: [Monday=Strategy, Tuesday=Psychology, ...]"
```

---

### 3. Force Your AI to Apply Models

When asking for advice, explicitly invoke learned models:

**Generic ask** (doesn't use mental models):
```
"Should I hire more people?"
```

**Strategic ask** (forces model application):
```
"Apply mental models from thinking-patterns.md: Should I hire more people? 
Consider: Brook's Law, Two-Pizza Teams, Scaling Challenges."
```

Your AI will:
1. Scan `thinking-patterns.md` for those patterns
2. Apply each lens to your question
3. Give you multi-dimensional strategic insight

---

## 📚 Sample Output

### Book: *Thinking, Fast and Slow* by Daniel Kahneman

**F.A.C.E.T. Analysis**:

```markdown
[F] Framework: Dual-Process Theory
Human cognition operates via two systems:
- System 1: Fast, automatic, emotional (95% of decisions)
- System 2: Slow, deliberate, rational (used only when forced)

Core mechanism: System 1 dominates by default → cognitive biases emerge 
when System 2 fails to override.

---

[A] Anchor Case: The Linda Problem
"Linda is 31, outspoken, very bright. She majored in philosophy.
Which is more probable?
1. Linda is a bank teller
2. Linda is a bank teller and active in the feminist movement"

Most people choose #2 (conjunction fallacy: P(A∩B) > P(A) is impossible).
System 1 says "feminist bank teller fits the story!"
System 2 (if engaged) knows #1 is mathematically more probable.

★ Why this sticks: Simple, vivid, reveals how smart people make dumb mistakes.

---

[C] Contradiction (What common sense dies)
Common sense: "People make rational decisions when given good information."
Kahneman: NO. Even experts (doctors, judges, investors) rely on System 1 
and commit systematic errors (availability bias, anchoring, sunk cost fallacy).

Implication: Education ≠ Better Decisions. Design systems to bypass bias.

---

[E] Edge (When this model fails)
Fragile assumptions:
1. Assumes humans can't improve System 1 (FALSE: deliberate practice CAN)
2. Assumes biases are universal (FALSE: cultural variation exists)
3. Overestimates System 2's reliability (it's lazy, not just slow)

When NOT to apply:
- Time-critical decisions (System 1 evolved for survival)
- Experts in narrow domains (chess masters' intuition IS reliable)

---

[T] Transfer (Mapped to YOUR context)
You're a product manager at 爱康国宾 building AI products.

Apply Dual-Process Theory:
1. User onboarding: Design for System 1 (one-click, zero thinking)
   ❌ Bad: "Please configure your health preferences (18 options)"
   ✅ Good: "Start now → We'll learn as you go"

2. Critical decisions: Force System 2 activation
   Example: AI recommends surgery → Add friction ("Review 3 times before confirming")

3. Team decision-making: Counteract groupthink
   Before approving feature X, ask: "What System 1 biases made us love this idea?"
   (Anchoring bias? Confirmation bias? Sunk cost?)

Concrete action THIS WEEK:
Audit your AI product's UI → Identify where users need System 1 ease vs. System 2 deliberation.
```

**Written to `thinking-patterns.md`**:
```markdown
## Dual-Process Theory (Kahneman)
**Source**: *Thinking, Fast and Slow*
**Core**: Human cognition = System 1 (fast/biased) + System 2 (slow/rational)
**Anchor Case**: Linda Problem (conjunction fallacy)
**Edge**: Fails when experts have calibrated intuition
**Domains**: Product design, decision-making, UX, risk assessment
**Cross-links**: → Nudge Theory, → Prospect Theory, → Bounded Rationality
```

---

## 🚀 Use Cases

### 1. Build a Personal Decision Framework Library
- **Who**: Founders, investors, strategists
- **How**: Process 1 book/week for 1 year = 52 mental models
- **Value**: Every future decision taps into 52 frameworks (compound thinking)

### 2. Team Learning System
- **Who**: Product teams, research labs
- **How**: Rotate book topics weekly, share F.A.C.E.T. analyses
- **Value**: Shared mental model language → Better collaboration

### 3. AI-Powered Reading Coach
- **Who**: Lifelong learners
- **How**: Your AI reads books YOU don't have time for, extracts models
- **Value**: You get the wisdom without reading 300 pages

### 4. Strategic Advisor Evolution
- **Who**: Anyone who wants smarter AI
- **How**: Let your AI read 100 classic books over months
- **Value**: Your AI becomes a Munger-like "latticework of mental models"

---

## 📂 File Structure

```
cognitive-forge/
├── SKILL.md                       # Main workflow definition
├── README.md                      # This file
└── references/
    ├── book-selection.md          # How book-scout filters quality
    ├── example-output.md          # Sample F.A.C.E.T. analyses
    └── knowledge-classification.md # How to categorize mental models
```

---

## 🎯 How This Differs from "Book Summary" Tools

| Feature | Cognitive Forge | Traditional Summary Tools |
|---------|----------------|---------------------------|
| **Goal** | Extract reusable mental model | Condense book content |
| **Focus** | **Transferable frameworks** | Facts and key points |
| **Permanence** | Written to thinking-patterns.md (forever) | Forgotten after reading |
| **Application** | Your AI applies it across domains | You read it once |
| **Personalization** | [T] Transfer maps to YOUR context | Generic for everyone |
| **Longevity** | Models compound over time | Summaries don't interact |

**Example**:
- **Summary tool**: "Antifragile says: embrace volatility, avoid fragility."
- **Cognitive Forge**: "Antifragility Test: Does this system GAIN from chaos? 
   Apply to: your product roadmap (yes/no), your hiring strategy (yes/no), 
   your investment portfolio (yes/no). Fragile assumption: requires optionality."

---

## 🛠️ Advanced Usage

### Multi-Book Cross-Analysis

```
Ask your AI: "Process 3 books on decision-making:
1. Thinking, Fast and Slow (Kahneman)
2. Superforecasting (Tetlock)
3. The Black Swan (Taleb)

Then cross-analyze: Where do their mental models agree? Conflict? Complement?"
```

Your AI will:
1. Process all 3 books (F.A.C.E.T. for each)
2. Write to thinking-patterns.md
3. Generate a meta-analysis showing how models interact

---

### Domain-Specific Model Curation

**For product managers**:
```
Schedule: Process 1 product/UX book per week
Topics: Jobs-to-be-Done, Hooked Model, Lean Startup, Design Thinking
Result: thinking-patterns.md becomes your PM playbook
```

**For investors**:
```
Topics: Mental Models (Munger), Antifragile (Taleb), Capital (Piketty)
Result: thinking-patterns.md becomes your investment decision framework
```

---

### Feishu/Notion Integration (Optional)

If you set `FEISHU_APP_TOKEN` or `NOTION_API_KEY`, the skill auto-uploads:
- Book title
- F.A.C.E.T. analysis
- Reading date
- Mental model tags

**Benefit**: Build a searchable knowledge base across your team.

---

## 🛠️ Troubleshooting

**"Book-scout can't find books on my topic"**:
- Try broader topics (e.g., "Psychology" instead of "Behavioral Economics of Crypto")
- Or specify a book directly: "Analyze: [Book Title] by [Author]"

**"F.A.C.E.T. analysis is too shallow"**:
- Your AI model may need extended reasoning (Claude Opus recommended)
- Ask: "Deep F.A.C.E.T. analysis with multiple examples"

**"How do I see what mental models my AI has learned?"**:
```bash
cat ~/.openclaw/workspace/memory/knowledge-base/thinking-patterns.md
```

**"My AI isn't applying learned models"**:
- Check if `thinking-patterns.md` is loaded in AGENTS.md (see section above)
- Explicitly ask: "Apply mental models from thinking-patterns.md to [question]"

---

## 📜 License

MIT-0 (No Attribution Required)

Use it, fork it, teach it — no strings attached.

---

## ⚠️ Important Notes

**Data Persistence**: This skill writes to `thinking-patterns.md` and `reading-history.json` in your workspace. These files persist across sessions.

**Optional Integration**: The "auto-load thinking-patterns.md" feature described in this README requires manual configuration in your `AGENTS.md`. The skill does NOT automatically modify your agent's behavior without your explicit setup.

**Export Tokens**: Environment variables (`FEISHU_APP_TOKEN`, `NOTION_API_KEY`) are entirely optional. The skill works perfectly fine without them (local-only mode).

---

## 🙌 Credits

Created by **汤圆 (Tangyuan)** for 雯姐's AI evolution journey.

**Inspired by**:
- Charlie Munger's "latticework of mental models"
- Nassim Taleb's antifragility & skin in the game
- Daniel Kahneman's dual-process theory
- Shane Parrish's Farnam Street framework

**Built with**:
- [`book-scout`](https://clawhub.ai/kedoupi/book-scout) — Quality book discovery
- [`mental-model-forge`](https://clawhub.ai/kedoupi/mental-model-forge) — F.A.C.E.T. analysis engine

---

## 📣 Feedback

This skill is about **AI getting smarter over time**. If you've processed 50+ books and want to share what your AI has learned, ping `@KeDOuPi` on ClawHub!

**Star this skill** if your AI is now wiser than you! ⭐🧠
