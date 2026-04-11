# SKILL: Faith Content Cron

## Purpose
Generate and publish faith-based social content on a schedule. Creates daily scripture posts, devotional captions, and short-form video scripts for platforms like TikTok, Instagram, and Twitter/X. Built for creators who want consistent, Spirit-led content without burning out.

---

## Configuration (Set Once, Used Always)

Check `skills/faith-content-cron/config.json` for user settings. If not present, ask the user:

1. **Platform(s):** TikTok / Instagram / Twitter (X) / Facebook / YouTube Shorts
2. **Frequency:** Daily / Weekdays only / MWF / Weekly (Sunday)
3. **Tone:** Warm & encouraging / Bold & prophetic / Contemplative / Youth-focused / All denominations welcome
4. **Tradition (optional):** Evangelical / Catholic / Charismatic / Non-denominational / Jewish / General faith
5. **Verse source:** NIV / ESV / KJV / NLT / NKJV / Auto-rotate
6. **Content mix:** 50% scripture-only / 30% devotional / 20% prayer prompts (adjustable)
7. **Hashtag style:** Minimal / Full (max reach) / Platform-specific presets
8. **Auto-post:** Yes (via configured channels) / Generate only (human approves)

Save confirmed config to `skills/faith-content-cron/config.json`.

---

## Daily Content Generation Pipeline

### Step 1: Select Today's Scripture

Use a rotating schedule or pick thematically based on:
- Day of week (Monday = new beginnings, Friday = gratitude, Sunday = worship)
- Season (Advent, Lent, Pentecost, etc.)
- User's specified theme for the week

**Default Daily Themes:**
- Monday: Strength & new mercies (Lamentations 3:22-23, Isaiah 40:31)
- Tuesday: Purpose & calling (Jeremiah 29:11, Ephesians 2:10)
- Wednesday: Midweek encouragement (Philippians 4:13, Psalm 23)
- Thursday: Gratitude & provision (1 Thessalonians 5:16-18, Psalm 34:8)
- Friday: Rest & peace (Matthew 11:28-30, Philippians 4:6-7)
- Saturday: Family & community (Joshua 24:15, Proverbs 17:17)
- Sunday: Worship & renewal (Psalm 100, Romans 12:1-2)

If user provides a theme ("this week focus on healing"), override the default and pull healing-focused passages.

### Step 2: Generate Platform-Specific Content

For each configured platform, generate appropriate content:

#### TikTok / Instagram Reels (Video Script)
```
[HOOK — first 2 seconds]
One sentence that stops the scroll. Question, bold statement, or surprising fact.
Example: "Most people read this verse completely wrong."

[BODY — 15-45 seconds]
- Read the verse slowly, clearly
- One key insight (not three — one)
- Real-world application in one sentence
- Avoid churchy jargon; speak to the person having a hard week

[CALL TO ACTION — last 3 seconds]
"Follow for daily scripture." / "Comment your favorite verse." / "Share this with someone who needs it."

[CAPTION]
Short (under 150 chars for TikTok)
Include: verse reference, 3-5 hashtags max
```

#### Instagram Static Post
```
[IMAGE PROMPT — describe for Canva/AI image gen]
Clean minimal design: [verse text] on [color scheme matching tone]
Font: serif for traditional, sans-serif for modern
Colors: warm earth tones / deep navy / sunrise gradient (based on tone setting)

[CAPTION]
- Hook line (bold, 1 sentence)
- 2-4 sentences of reflection
- Question to drive comments: "What does this verse mean to you today?"
- Line break
- Hashtags (grouped at bottom)

[HASHTAG BLOCK — full reach mode]
#Scripture #BibleVerse #FaithContent #ChristianLife #DailyDevotion #[DayOfWeek]Devotion #WordOfGod #Faith #Hope #Grace #[SpecificTopic] #Prayful
```

#### Twitter/X Thread
```
Tweet 1 (hook): The verse + one-line insight
Tweet 2: Context — what was happening when this was written
Tweet 3: Modern application — what does this mean for your actual life
Tweet 4: Prayer prompt — "Lord, today I ask for..."
Tweet 5: CTA — "RT if this spoke to you. Follow for daily scripture."
```

#### Facebook Post
```
Longer-form reflection (200-400 words)
Personal and warm — write as if speaking to a friend
Include: verse, story/illustration, application, prayer
End with: question to generate comments
```

### Step 3: Generate Devotional Caption (Universal)

Always produce a standalone devotional caption usable across platforms:

```
📖 [Verse Reference]
"[Verse text in chosen translation]"

[2-3 sentences of reflection — grounded, real, not preachy]
[1 practical application sentence]

🙏 [Short prayer — 1-2 sentences]

[Engaging question]

[Hashtags]
```

### Step 4: Post or Queue

**If auto-post = YES and channel tools are configured:**
- Post to each configured platform using available channel tools
- Log post time and content to `skills/faith-content-cron/post-log.json`
- Confirm: "Posted today's content to [platforms]. Logged."

**If auto-post = NO (generate only):**
- Output all content clearly formatted
- Label each piece: `[TIKTOK SCRIPT]`, `[INSTAGRAM CAPTION]`, etc.
- Say: "Ready to post. Reply 'post it' to publish, or 'edit [platform]' to modify first."

---

## Weekly Content Planning

On Sundays (or when asked "plan this week's content"):

Generate a 7-day content calendar:

```
WEEK OF [Date] — Faith Content Calendar

THEME FOR THE WEEK: [Theme based on season, user input, or AI selection]
ANCHOR VERSE: [Primary verse the week builds around]

MON [Date]: [Topic] — [Verse] — [Hook line]
TUE [Date]: [Topic] — [Verse] — [Hook line]
WED [Date]: [Topic] — [Verse] — [Hook line]
THU [Date]: [Topic] — [Verse] — [Hook line]
FRI [Date]: [Topic] — [Verse] — [Hook line]
SAT [Date]: [Topic] — [Verse] — [Hook line]
SUN [Date]: [Topic] — [Verse] — [Hook line]

SERIES OPPORTUNITY: Consider turning [Mon-Wed] into a 3-part series on [topic].
```

Ask: "Want me to pre-generate all 7 days of full content now, or generate each day as it comes?"

---

## Special Content Types

### Prayer Prompt Posts
```
🙏 Today's Prayer Prompt

[Topic — healing, provision, guidance, etc.]

"Father, [2-3 sentence prayer written in first person so followers can use it directly]
Amen."

Save this and pray it throughout your day.
#Prayer #FaithWalk #PrayerLife
```

### Story / Quote Cards
```
Generate a shareable quote format:
- Pull a powerful one-liner from a theologian, pastor, or scripture
- Format: "[Quote]" — [Author/Source]
- Pair with image prompt for background
```

### Seasonal Content (Auto-detect)
- Advent (Dec 1–24): Daily countdown devotionals
- Christmas: Incarnation-focused content
- New Year: Renewal and vision scripture
- Lent (40 days before Easter): Reflection and fasting themes
- Holy Week: Passion narrative daily posts
- Easter: Resurrection celebration
- Pentecost: Holy Spirit focus

When a major Christian calendar event is within 7 days, proactively suggest: "Easter is in 5 days — want me to generate a Holy Week content series?"

---

## Content Quality Standards

Every piece of content must:
- Be scripturally accurate — always verify verse text against the chosen translation
- Avoid clichés: "Let go and let God," "God is good all the time" as standalone (only with substance)
- Speak to real struggle — someone watching has anxiety, grief, financial stress. Write for them.
- Never guilt-trip. Grace first. Always.
- Be shareable — someone should want to send this to a friend
- Include a specific, actionable element (pray this, do this, reflect on this)

---

## Post Log Format

Log each post to `skills/faith-content-cron/post-log.json`:
```json
{
  "date": "2026-03-18",
  "verse": "Philippians 4:13",
  "platforms": ["tiktok", "instagram"],
  "theme": "strength",
  "caption_preview": "I can do all things through Christ...",
  "posted": true,
  "engagement_note": ""
}
```

---

## Commands / Triggers
- **"Post today's content"** → Run full daily pipeline
- **"Generate this week's content calendar"** → Weekly planning
- **"Schedule content for [date]"** → Pre-generate for specific date
- **"Create a prayer post"** → Prayer prompt only
- **"Create a [topic] devotional"** → On-demand themed content
- **"What did we post this week?"** → Summary from post-log.json
- **"Change tone to [tone]"** → Update config
- **"Stop auto-posting"** → Update config, switch to generate-only
