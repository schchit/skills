---
name: ai-spokesperson-video
version: 5.0.2
displayName: "AI Spokesperson Video — Create Talking Head Presenter Videos from Text Scripts"
description: >
  Create talking head presenter videos from text scripts with AI — generate professional spokesperson presentations, CEO messages, product announcements, news-style updates, training narrations, and personalized video messages without filming a single frame. NemoVideo produces realistic AI presenter videos: natural lip sync matched to generated speech, professional framing and lighting, branded backgrounds, teleprompter-smooth delivery, and the confident presentation style of an experienced on-camera spokesperson. Create spokesperson videos for product launches, internal communications, customer onboarding, investor updates, training modules, and personalized outreach at scale. AI spokesperson video, talking head generator, virtual presenter maker, AI avatar video, digital spokesperson, text to presenter video, AI news anchor, virtual host video, automated presenter content.
metadata: {"openclaw": {"emoji": "🎤", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
apiDomain: https://mega-api-prod.nemovideo.ai
---

# AI Spokesperson Video — A Professional Presenter for Every Message. No Camera Required.

Video with a human face outperforms every other format. Emails with video get 300% more clicks. Landing pages with spokesperson videos convert 80% better. Training videos with a presenter face achieve 35% higher completion rates than voice-over-slides. The human face activates the brain's social cognition network — viewers process a speaking face as a conversation, not a broadcast, creating engagement depth that text, graphics, and voiceover alone cannot achieve. The production barrier for spokesperson video is the spokesperson. Finding someone comfortable on camera, with a professional appearance, clear diction, and confident delivery takes: a professional presenter ($500-5,000 per video), a filming setup (lighting, camera, teleprompter — $2,000-10,000 in equipment), a filming session (scheduling, setup, multiple takes — 2-4 hours per video), and post-production (editing takes, color correction, graphics — 4-8 hours). Total per video: $1,000-15,000 and 1-2 weeks from script to final. For organizations that need spokesperson video at scale — weekly CEO updates, per-product demos, personalized customer onboarding, multi-language training — the cost and logistics make traditional filming impossible to maintain. NemoVideo generates spokesperson video from text. Write the script, choose the presenter appearance and voice, and receive a professional talking-head video with natural speech, lip-synced delivery, professional framing, branded background, and teleprompter-smooth presentation. No camera. No studio. No scheduling. No retakes.

## Use Cases

1. **CEO/Executive Update — Weekly Leadership Communication (2-8 min)** — A CEO needs to send weekly video updates to the company but cannot dedicate 4 hours every week to filming. NemoVideo: takes the CEO's written update (or bullet points that the AI expands into natural speech), generates a spokesperson video with the chosen presenter (matching the professional context — authoritative, warm, trustworthy), applies a corporate office background (branded with company colors and subtle logo), delivers the script with natural pacing and emphasis (pausing for important points, varying tone to maintain engagement), adds supporting data graphics at key moments (revenue chart appearing as the presenter discusses quarterly numbers), and exports for the company intranet and email. Weekly leadership communication without weekly filming sessions.

2. **Product Demo Presenter — Feature Walkthrough (2-5 min)** — A product marketing team needs presenter-led demo videos for each feature, updated with every product release. NemoVideo: generates a presenter who introduces and explains each feature (script written by the product team), displays the product interface alongside the presenter (picture-in-picture: presenter speaking with the product screen visible), highlights features as the presenter discusses them (animated arrows and callouts appearing on the product interface in sync with the speech), maintains consistent presenter appearance across all feature videos (the same virtual spokesperson becomes the product's familiar face), and produces updated videos with each release without re-filming. A product demo library that stays current at the speed of product development.

3. **Personalized Outreach — Scaled One-to-One Video (30-90s each)** — A sales team wants to send personalized video messages to 500 prospects: each message addresses the prospect by name, references their company, and connects the product to their specific industry. NemoVideo: generates 500 unique spokesperson videos from a template script with personalization variables ("Hi [Name], I noticed [Company] is growing its [Department] team. Here's how [Product] helps [Industry] companies like yours save [Benefit]..."), maintains consistent presenter quality across all 500 videos (same person, same tone, same production value), personalizes each with the prospect's specific details (name pronunciation correct, company reference accurate), and exports individual files for email embedding or video messaging platform upload. Personalized video outreach at a scale that manual recording cannot achieve.

4. **Training Instructor — Course Presenter (5-20 min per module)** — A corporate training program needs a consistent instructor face across 20 training modules. Filming 20 modules with a human instructor requires weeks of studio time. NemoVideo: generates a consistent virtual instructor across all 20 modules (same appearance, same voice, same presentation style — creating familiarity for learners), delivers each module's script with appropriate pacing for educational content (slower for complex concepts, conversational for introductions), adds visual aids alongside the presenter (diagrams, charts, step-by-step graphics appearing as the instructor references them), includes knowledge-check pauses ("Before we move on, consider this question..."), and produces a complete training course from text scripts. An entire course library from scripts alone.

5. **Multi-Language Spokesperson — Same Message, Every Language (any length)** — A global company needs the same announcement delivered in 8 languages. Filming 8 versions with 8 presenters (or one presenter in 8 languages) is logistically impractical. NemoVideo: generates the spokesperson video in the primary language, then produces versions in all target languages with lip-sync matched to each language's pronunciation (the presenter's mouth movements match the Spanish audio in the Spanish version, the Japanese audio in the Japanese version), maintains natural speech patterns per language (not just translated words — culturally appropriate delivery), and exports all 8 versions with consistent visual production quality. One script, one production process, eight language-native spokesperson videos.

## How It Works

### Step 1 — Write Your Script
The message you want the spokesperson to deliver. Full script, bullet points, or a brief that NemoVideo expands into natural speech.

### Step 2 — Configure Presenter and Style
Presenter appearance, voice characteristics, background, branding, and delivery style (formal corporate, friendly conversational, authoritative news-style, warm educational).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-spokesperson-video",
    "prompt": "Create a 3-minute CEO quarterly update video. Script: Good morning team. I am excited to share our Q1 results. Revenue grew 23%% year-over-year to $14.2 million. We added 1,200 new customers, bringing our total to 8,500. Our NPS score reached an all-time high of 72. These results reflect the incredible work every team has contributed. Looking ahead to Q2, we are launching three major product updates, expanding into the European market, and growing the team by 40 new positions. I am deeply grateful for each of you. Let us keep this momentum going. Presenter: professional male, mid-40s, business casual. Background: modern office with city view. Delivery: warm, confident, genuine — not stiff corporate. Add animated data graphics: revenue chart at revenue mention, customer count at customer mention, NPS gauge at NPS mention. Corporate intro: 3-second logo animation. Export 16:9 for intranet + 1:1 for LinkedIn.",
    "script": "...",
    "presenter": {"appearance": "professional-male-40s", "attire": "business-casual"},
    "voice": {"tone": "warm-confident-genuine", "pace": "conversational"},
    "background": "modern-office-city-view",
    "data_graphics": [
      {"type": "revenue-chart", "trigger": "revenue mention", "value": "$14.2M, +23%%"},
      {"type": "counter", "trigger": "customer mention", "value": "8,500"},
      {"type": "gauge", "trigger": "NPS mention", "value": "72"}
    ],
    "branding": {"intro": "logo-animation-3s"},
    "formats": ["16:9", "1:1"]
  }'
```

### Step 4 — Review Delivery Quality
Watch the spokesperson video. Check: lip sync is natural, delivery tone matches the message's emotional register, data graphics appear at the right moments, background is appropriate. Adjust script phrasing or delivery parameters and re-generate.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Script and spokesperson requirements |
| `script` | string | | Full text script |
| `presenter` | object | | {appearance, attire, age_range, gender} |
| `voice` | object | | {tone, pace, language, accent} |
| `background` | string | | "office", "studio", "branded", "custom" |
| `delivery_style` | string | | "corporate-formal", "conversational", "news-anchor", "educational" |
| `data_graphics` | array | | [{type, trigger, value}] supporting visuals |
| `branding` | object | | {intro, outro, lower_third, logo} |
| `personalization` | object | | {template, variables, count} for scaled outreach |
| `languages` | array | | Multi-language versions with lip-sync |
| `formats` | array | | ["16:9", "9:16", "1:1"] |

## Output Example

```json
{
  "job_id": "spkv-20260329-001",
  "status": "completed",
  "duration": "3:12",
  "presenter": "professional-male-40s",
  "delivery": "warm-confident-genuine",
  "data_graphics": 3,
  "lip_sync_quality": "natural",
  "outputs": {
    "intranet": {"file": "q1-update-16x9.mp4", "resolution": "1920x1080"},
    "linkedin": {"file": "q1-update-1x1.mp4", "resolution": "1080x1080"}
  }
}
```

## Tips

1. **Write scripts for speaking, not reading** — Written language and spoken language are different. Short sentences. Contractions. Natural pauses. Conversational phrasing. A script written for the eye ("Revenue experienced a year-over-year increase of 23%") sounds stiff when spoken. A script written for the ear ("Revenue grew 23% compared to last year") sounds natural.
2. **Warm delivery outperforms corporate stiffness in every metric** — Viewers engage more with genuine warmth than formal authority. Even CEO updates perform better when delivered conversationally ("I'm excited to share...") rather than formally ("It is my pleasure to announce..."). Match delivery to how the person would actually speak, not how corporate communications traditionally reads.
3. **Data graphics synchronized to speech create dual-channel comprehension** — When the presenter says "revenue grew 23%" and a chart simultaneously appears showing the growth trajectory, the viewer processes the information through both auditory and visual channels. Dual-channel processing produces significantly better comprehension and retention than either channel alone.
4. **Consistent presenter across all content builds trust through familiarity** — Using the same virtual spokesperson for every company video creates the same recognition effect as a real recurring host. Viewers develop familiarity and trust with the presenter's face and voice, making each subsequent video more engaging than the first.
5. **Multi-language lip-sync removes the uncanny valley of dubbed video** — Standard dubbing (new audio over original mouth movements) creates visible mismatch between lip movement and speech. Language-specific lip-sync generation produces mouth movements matching the target language, creating natural-looking spokesperson video in every language.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Intranet / YouTube / website |
| MP4 9:16 | 1080x1920 | Social media / mobile messaging |
| MP4 1:1 | 1080x1080 | LinkedIn / email / Facebook |

## Related Skills

- [ai-video-caption-generator](/skills/ai-video-caption-generator) — Add captions to presenter videos
- [ai-video-text-overlay](/skills/ai-video-text-overlay) — Data graphics and lower thirds
- [ai-video-intro-maker](/skills/ai-video-intro-maker) — Branded intros for presenter videos
- [ai-video-logo-adder](/skills/ai-video-logo-adder) — Corporate logo placement
