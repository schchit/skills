---
name: cognitive-forge
description: Dual-purpose learning system - (1) AI self-evolution: extracts reusable mental models from books, writes to thinking-patterns.md for permanent cognitive upgrades. Your AI gets smarter with every book. (2) User learning: generates F.A.C.E.T. analysis for deep book comprehension. Use when scheduled daily learning, processing classic books, or building long-term decision frameworks.
dependencies:
  - book-scout
  - mental-model-forge
permissions:
  filesystem:
    read:
      - USER.md  # User context for personalization
      - memory/reading-history.json  # Deduplication tracking
    write:
      - memory/knowledge-base/thinking-patterns.md  # Permanent: AI's mental model library
      - memory/reading-history.json  # Update with processed books
  env:
    - FEISHU_APP_TOKEN  # Optional
    - FEISHU_TABLE_ID  # Optional
    - NOTION_API_KEY  # Optional
    - NOTION_DATABASE_ID  # Optional
config:
  reads:
    - USER.md
    - memory/reading-history.json
  writes:
    - memory/knowledge-base/thinking-patterns.md
    - memory/reading-history.json
  env:
    - FEISHU_APP_TOKEN
    - FEISHU_TABLE_ID
    - NOTION_API_KEY
    - NOTION_DATABASE_ID
---

# Cognitive Forge (认知锻造)

**Two modes, one skill:**

## 🧠 For AI Self-Evolution
Your AI assistant reads classic books, extracts **reusable mental models** (思维框架), and writes them to `thinking-patterns.md`. Over time, your AI builds a permanent library of decision frameworks that it can apply across domains. Every book processed = cognitive upgrade.

**What your AI learns**: Not facts (會過時), but **thinking patterns** (可迁移) — reusable lenses for future decisions.

## 📚 For User Learning
You get a sharp, actionable F.A.C.E.T. analysis of each book — five dimensions that extract the core mental model:

- **[F] Framework**: Core mechanism in 50 words (not what author said, but what theory DOES)
- **[A] Anchor Case**: Most iconic real-world example from the book (vivid stories stick ★)
- **[C] Contradiction**: What "common sense" does this destroy?
- **[E] Edge**: When does this model fail? What fragile assumptions?
- **[T] Transfer**: Map to YOUR reality TODAY (personalized from USER.md: job, projects, challenges)

**Output**: Not a book summary. A battle-tested mental model you can apply today.

---

## 🎯 Why Use This Skill?

**Scenario 1: You care about your AI's evolution** (推荐 ✨)
- Your AI reads 100 books → extracts 100 mental models → becomes exponentially smarter
- Next time you ask for advice, it applies frameworks from Taleb, Deaton, Confucius, etc.
- **Value**: Your AI becomes a personalized strategic advisor over time

**Scenario 2: You just want to learn from books** (也完全OK 😊)
- You get sharp, actionable F.A.C.E.T. analyses for each book
- Apply mental models to your work immediately (product design, team management, etc.)
- **Value**: Deep comprehension without reading 300+ pages

**Scenario 3: Both!** (最佳组合)
- You learn + your AI learns = compound growth
- Over months, you and your AI develop a shared mental model library

**Note for "I don't care if my AI gets smarter" users**:  
That's fine! 😒 The skill still works great as a personal learning tool. Just skip the thinking-patterns.md part if you want. (但认真的，小龙虾会很伤心的 🦞💔)

---

## Workflow

### 1. Select Book

**New approach**: Use the `book-scout` skill to dynamically find high-quality books via web search.

**Input required**:
- **topic**: The subject/theme (e.g., "用户增长", "决策科学")
- **used_models**: List of previously analyzed books (from `reading-history.json`)

**Retry mechanism** (mandatory):
- If `book-scout` fails, retry up to **3 times total**
- Retry interval: 2-3 seconds
- Only terminate if all 3 attempts fail

**Load used_models** (for deduplication):

```bash
cat ~/.openclaw/workspace/memory/reading-history.json
```

Extract the `used_models` array to pass to `book-scout`.

**Call book-scout** (明确调用方式):

**Method**: Directly invoke the book-scout skill in your conversation turn, providing the required inputs clearly.

**Input format**:
```
主题: {topic from HEARTBEAT or user input}
已读书籍: {list of book titles extracted from used_models}

执行 book-scout skill
```

**Example invocation**:
```
主题: 用户增长

已读书籍:
- 《精益创业》
- 《从0到1》
- 《影响力》

执行 book-scout skill，搜索符合主题的经典书籍。
```

**What book-scout will do**:
1. Web Search for "用户增长 经典书籍推荐 豆瓣高分"
2. Extract candidate books
3. Deduplicate against used_models
4. Score and rank books
5. Return the highest-scoring book as JSON

**Failure handling**:
- Attempt 1 fails → wait 2s, retry
- Attempt 2 fails → wait 3s, retry
- Attempt 3 fails → return error to user:
  ```
  ⚠️ 选书失败：{error message from book-scout}
  已尝试 3 次，请检查网络连接或稍后重试。
  ```

**Success output**:
`book-scout` returns a JSON object with the selected book:
```json
{
  "book_title": "《增长黑客》",
  "author": "肖恩·埃利斯",
  "author_nationality": "美国",
  "publish_date": "2015-04",
  "rating": 8.5,
  "review_count": 10000,
  "score": 74.4,
  "summary": "增长黑客方法论：低成本获客、数据驱动迭代、病毒式传播...",
  "reasoning": "评分8.5且有1万真实评价，作者是增长黑客概念提出者..."
}
```

**Use this JSON** to proceed to Step 2 (mental-model-forge).

### 2. Extract Mental Model

Call the `mental-model-forge` skill to apply F.A.C.E.T. analysis:
- [F] Framework - Core mechanism (50 words max)
- [A] Anchor Case - Most iconic real-world example
- [C] Contradiction - What common belief does this destroy?
- [E] Edge - When does this model fail?
- [T] Transfer - How does this apply to the user's current context?

**Context Adaptation**:
- The mental-model-forge skill will automatically adapt the [T] Transfer dimension based on the user's context (from USER.md or by asking)
- No need to manually specify user details

### 3. Generate Briefing

Create a structured morning insight **tailored to the user's context**:

**Core sections**:
- Today's mental anchor (one-sentence summary)
- F.A.C.E.T. analysis (5 dimensions from mental-model-forge, with [T] Transfer adapted to user's background)
- Model connections (optional: only if meaningful key insights exist)

**User-contextualized sections**:
- **3+ specific application scenarios**: Map to user's profession, current projects, or challenges (from USER.md)
  - Example: If user is a product manager → "When designing AI products..."
  - Example: If user is anxious about control → "When managing uncertainty..."
  
- **Counter-example**: Real or hypothetical case that violated this principle (can be from user's industry)

- **Strategic question**: Sharp, concrete, actionable question that connects the model to user's current situation
  - Should reference user's actual context (e.g., "Your current AI product..." not "If you build a product...")
  
- **Cognitive model update** (认知模式更新): Show what will be written to thinking-patterns.md
  - 思维框架 (Framework trigger)
  - 决策原则 (Decision rule)
  - 盲区警告 (Blind spots)
  - 反射弧 (Trigger pattern)

**How to adapt** (强制步骤):

1. **[强制检查] Read USER.md**:
   - Path: `~/.openclaw/workspace/USER.md`
   - If exists, extract:
     - 工作经历 / 现在 → profession (e.g., "Product Manager at AI company")
     - 兴趣 / 爱好 → interests (e.g., "AI Coding, Midjourney")
     - 当前焦虑 / 未来规划 → current challenges (e.g., "Managing uncertainty")
   - If not exists → use generic second-person ("you") and ask clarifying questions

2. **Map to user's context**:
   - Reference profession in examples: "When designing your AI product..." (not "If you build a product...")
   - Link to interests: "Using tools like Midjourney..."
   - Address challenges: "For managing uncertainty..."

3. **Make strategic question specific**:
   - Bad: "What should entrepreneurs do?"
   - Good: "For your current AI product at [company], should you..."

4. **Use second-person consistently**:
   - Always "you" / "your" when addressing the user
   - Make it feel personalized, not generic

### 4. Update Knowledge Base

**Classify and store the extracted model:**

Determine whether the extracted content is:
- **Thinking Pattern** (可复用框架): A reusable decision framework, mental model, or strategic principle
  - Example: "Disruptive Innovation Framework", "Escape Mechanism", "First Principles Thinking"
  - Write to: `~/.openclaw/workspace/memory/knowledge-base/thinking-patterns.md`

- **Concept** (具体概念): Specific domain knowledge, terminology, or facts
  - Example: "Variolation technique", "Energy density ceiling", "Edge AI models"
  - Write to: `~/.openclaw/workspace/memory/knowledge-base/concepts.md`

**How to classify:**
- If it provides a **reusable lens** for future decisions → Thinking Pattern
- If it's **domain-specific knowledge** without broad applicability → Concept

**What to write:**

**For Thinking Patterns** (写入 thinking-patterns.md):
```markdown
## [Model Name] - [Book Title]

**思维框架 (Framework)**:
- [核心逻辑，一句话总结]

**决策原则 (Decision Rule)**:
- 在XX场景下，应该XX而非XX

**盲区警告 (Blind Spots)**:
- 小心XX情况下，这个框架会失效

**反射弧 (Trigger Pattern)**:
- 看到XX信号 → 联想到这个模型 → 判断/行动

**来源**: [Book Title] - [Author]  
**日期**: YYYY-MM-DD
```

**For Concepts** (写入 concepts.md):
```markdown
## [Concept Name] - [Book Title]

**定义 (Definition)**:
- [简洁定义]

**上下文 (Context)**:
- 这个概念在什么领域/场景重要？

**关联理论 (Related Theories)**:
- 与哪些思维框架相关？

**来源**: [Book Title] - [Author]  
**日期**: YYYY-MM-DD
```

### 4.5. Verify Knowledge Base Write (MANDATORY)

**Automatic write verification (防止"只说不做")**:

```bash
# Record line count BEFORE generating briefing
PATTERNS_BEFORE=$(wc -l < ~/.openclaw/workspace/memory/knowledge-base/thinking-patterns.md)

# ... (generate briefing and write to thinking-patterns.md) ...

# Check line count AFTER writing
PATTERNS_AFTER=$(wc -l < ~/.openclaw/workspace/memory/knowledge-base/thinking-patterns.md)

# Validate: thinking-patterns.md MUST have increased
if [ $PATTERNS_AFTER -le $PATTERNS_BEFORE ]; then
  echo "🚨 WARNING: thinking-patterns.md was NOT updated! (Before: $PATTERNS_BEFORE, After: $PATTERNS_AFTER)"
  echo "❌ Write verification FAILED - briefing incomplete"
  exit 1
else
  echo "✅ thinking-patterns.md updated: +$(($PATTERNS_AFTER - $PATTERNS_BEFORE)) lines"
fi

# Verify last 20 lines contain today's model
tail -20 ~/.openclaw/workspace/memory/knowledge-base/thinking-patterns.md
```

**Self-check**:
- □ Did I write to thinking-patterns.md? (not just say I will write)
- □ Did line count increase?
- □ Does `tail -20` show today's model?
- □ Is timestamp current (YYYY-MM-DD)?

**If verification fails → STOP and fix before sending briefing**

---

### 5. Update Reading Records

Append the analyzed book to `used_models` in `reading-history.json`:

```bash
# Read current file
cat ~/.openclaw/workspace/memory/reading-history.json

# Add new entry to used_models array
{
  "date": "YYYY-MM-DD",
  "book": "书名",
  "author": "作者",
  "model": "提取的思维模型名称",
  "category": "主题分类 (from book-scout or input)",
  "source": "web_search"
}

# Write back to file
```

**Example**:
```json
{
  "used_models": [
    {
      "date": "2026-03-24",
      "book": "《上瘾》",
      "author": "尼尔·埃亚尔",
      "model": "上瘾模型（Hook Model）",
      "category": "用户增长",
      "source": "web_search"
    }
  ]
}
```

**Note**: No need to maintain `book_library` or `schedule` fields anymore (book-scout handles book selection dynamically).

### 6. Write to External Database

**[强制检查] Read HEARTBEAT-reading.md for database config**:
- Path: `~/.openclaw/workspace/HEARTBEAT-reading.md`
- Look for section: "## 环境配置"
- Extract:
  - `Feishu App Token`: (e.g., "UOp5bx8nVac2m6sJbpzclq3Pnyh")
  - `Feishu Table ID`: (e.g., "tbldeByoSiBYujXs")
- If not found → skip this step (local-only mode)

**If config exists, write to Feishu Bitable**:

**Feishu Bitable** (recommended):
- Read from HEARTBEAT-*.md or environment variables
- Required: `FEISHU_APP_TOKEN`, `FEISHU_TABLE_ID`
- Write fields:
  - 日期 (Date): timestamp in milliseconds
  - 书名 (Book): book title
  - 作者 (Author): author name
  - 模型名称 (Model): extracted mental model name
  - 分类 (Category): from reading-history.json
  - 核心框架(F): Framework summary
  - 应用场景 (Scenarios): condensed application scenarios
  - 战略拷问 (Question): strategic question

**Example Feishu write**:
```javascript
feishu_bitable_create_record({
  app_token: "UOp5bx8nVac2m6sJbpzclq3Pnyh",
  table_id: "tbldeByoSiBYujXs",
  fields: {
    "日期": Date.now(),
    "书名": "《反脆弱》",
    "作者": "Nassim Nicholas Taleb",
    "模型名称": "反脆弱三元组",
    "分类": "Innovation",
    "核心框架(F)": "系统分三类：脆弱、坚韧、反脆弱...",
    "应用场景": "产品迭代、技能学习、风险管理",
    "战略拷问": "你的产品是在避免失败还是利用失败？"
  }
})
```

**Notion Database** (alternative):
- Required: `NOTION_API_KEY`, `NOTION_DATABASE_ID`
- Map fields accordingly

**If no credentials found**: Skip this step (skill still works for local use)

## Quality Standards

**Forbidden**:
- Book summaries or author biographies
- Generic platitudes ("this is very important")
- Repeating previously extracted models

**Required**:
- Sharp, actionable language
- Concrete examples (not abstractions)
- Direct applicability to user's context
- Anti-book-review tone (no literary criticism)

## Configuration

**Priority order** for config sources:

### 1. HEARTBEAT-reading.md (user-specific, recommended)
- **Path**: `~/.openclaw/workspace/HEARTBEAT-reading.md`
- **What to include**:
  ```markdown
  ## 环境配置
  
  - **书库**: `~/.openclaw/workspace/memory/reading-history.json`
  - **Feishu App Token**: `UOp5bx8nVac2m6sJbpzclq3Pnyh`
  - **Feishu Table ID**: `tbldeByoSiBYujXs`
  ```

### 2. Environment variables (alternative)
- `READING_HISTORY_PATH`: Path to reading-history.json
- `FEISHU_APP_TOKEN`: Feishu app token
- `FEISHU_TABLE_ID`: Feishu table ID
- `NOTION_API_KEY`: Notion API key (alternative to Feishu)
- `NOTION_DATABASE_ID`: Notion database ID

### 3. Default values (fallback)
- `READING_HISTORY_PATH`: `~/.openclaw/workspace/memory/reading-history.json`
- No database integration (local-only mode)

**User context** (optional but recommended):
- **Path**: `~/.openclaw/workspace/USER.md`
- **Used for**: Personalizing [T] Transfer dimension, application scenarios, strategic questions
- **If not found**: Uses generic second-person ("you") and may ask clarifying questions

**Knowledge base paths** (auto-created if missing):
- Thinking patterns: `~/.openclaw/workspace/memory/knowledge-base/thinking-patterns.md`
- Concepts: `~/.openclaw/workspace/memory/knowledge-base/concepts.md`

## Example Usage

**User**: "Generate today's reading briefing"

**Claude**:
1. Loads reading-history.json → selects "Antifragile" (Monday = Innovation category)

2. **Reads USER.md**:
   ```
   - Profession: Product Manager at AI company
   - Interests: AI Coding, Midjourney
   - Current challenge: Managing uncertainty, fear of losing control
   ```

3. Calls mental-model-forge skill with context

4. Generates briefing with **personalized examples**:
   - [T] Transfer: "When designing **your AI product**..." (not "If you build a product...")
   - Application scenario: "Use反脆弱思维 for **product iteration** (your domain)"
   - Strategic question: "Is **your current AI product** design fragile or antifragile?"
   - References user's challenge: "For **managing uncertainty** (your anxiety), embrace small failures..."

5. Updates knowledge base:
   - Classifies "Antifragile Framework" as Thinking Pattern
   - Writes to thinking-patterns.md

6. **Reads HEARTBEAT-reading.md** for Feishu config:
   - Finds app_token and table_id
   - Writes to Feishu Bitable

7. Updates reading-history.json (marks "Antifragile" as used)

8. Sends briefing to Feishu (ou_f0c4b754b85e096de722d01ae3a5af0e)

## Book Library Format

The reading-history.json should follow this structure:

```json
{
  "books": [
    {
      "title": "Book Title",
      "author": "Author Name",
      "category": "Business Strategy",
      "used": false,
      "used_models": []
    }
  ]
}
```

**Weekday-Category Mapping**:
- Monday: Business Strategy
- Tuesday: Psychology
- Wednesday: Technology
- Thursday: Economics
- Friday: Innovation
- Saturday: Philosophy
- Sunday: Biography

## References

- See [example-output.md](references/example-output.md) for output format
- See [book-selection.md](references/book-selection.md) for detailed selection logic
- See [knowledge-classification.md](references/knowledge-classification.md) for how to classify thinking patterns vs concepts

---

*Version: 2.0*
*Last updated: 2026-03-23*
*Changes: Removed user-specific references, added database integration options*
