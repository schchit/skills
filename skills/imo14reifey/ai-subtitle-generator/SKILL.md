---
name: ai-subtitle-generator
version: "10.0.1"
displayName: "AI Subtitle Generator — Generate Accurate Subtitles and Closed Captions for Any Video"
description: >
  You just finished a thirty-minute interview with a founder who switches between English and Mandarin mid-sentence. Your editor needs subtitles by morning. The freelancer you usually hire quoted three days and two hundred dollars. What if you could upload the raw footage right now, specify both languages, and have publishable subtitles waiting in your inbox before your next coffee? That is what AI Subtitle Generator does. It listens to every word regardless of accent or language switch, assigns each phrase to the correct speaker, timestamps at the syllable level so lips and text never drift apart, and outputs whatever format your editor or platform requires. No glossary needed — the model infers technical terms from context. No style sheet needed — pick a preset or define your own.
metadata: {"openclaw": {"emoji": "📝", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Subtitle Generator — Professional Subtitles from Any Audio in Any Language

Subtitles have transcended their origin as an accessibility tool to become the dominant mode of video consumption globally. The numbers tell the story: 85% of social media video is watched without sound. 80% of Netflix viewers in non-English markets use subtitles. YouTube reports that videos with subtitles receive 7.3% more views than identical content without. The EU's European Accessibility Act (effective 2025) mandates subtitles for commercial video content. The US ADA increasingly requires captioning for public-facing digital content. Subtitles are simultaneously an accessibility requirement, an engagement multiplier, a global reach enabler, and an SEO tool. The quality spectrum of subtitling is vast. At one end: auto-generated platform captions with 80-85% accuracy, sentence-level timing, fixed styling, and no speaker differentiation. At the other: professional human subtitling at $3-8 per minute of video, 99%+ accuracy, word-level timing, custom styling, and full speaker identification — at 24-48 hour turnaround and costs that make library-wide subtitling prohibitive. NemoVideo occupies the sweet spot: 98%+ accuracy approaching professional human quality, word-level timing precision, fully customizable styling, multi-speaker differentiation, 50+ language translation, and instant turnaround — at a fraction of human subtitling cost. Professional subtitling quality at auto-caption speed and price.

## Use Cases

1. **Content Creator Subtitles — Styled for Engagement (any length)** — A creator's YouTube video, podcast episode, or course lesson needs subtitles that serve both accessibility and engagement. NemoVideo: transcribes with 98%+ accuracy (handling the creator's specific vocabulary, recurring phrases, and brand terminology after minimal training), applies the creator's branded subtitle style (specific font, colors matching channel branding, animation matching content energy), positions within platform-appropriate safe zones, generates word-level timing for animated display (each word appearing or highlighting as spoken), and exports both embedded-subtitle video (for social platforms where caption upload is limited) and standalone subtitle files (SRT for YouTube, VTT for web players). Subtitles that serve deaf viewers, muted scrollers, non-native speakers, and engagement metrics simultaneously.

2. **Corporate Multi-Language Subtitling — Global Communications (any length)** — A multinational company produces a product launch video in English that needs subtitles in Spanish, French, German, Japanese, Mandarin, Portuguese, and Arabic for global distribution. NemoVideo: transcribes the English source, translates to all 7 languages using context-aware AI (understanding industry terminology, product names, and corporate language conventions), adjusts subtitle timing per language (accommodating character count differences — German subtitles need more display time than Japanese for equivalent content), handles right-to-left rendering for Arabic (proper RTL text display with correct line breaking), maintains consistent visual styling across all languages, and exports subtitle files compatible with the company's video hosting platform. One video accessible to a global workforce and customer base.

3. **Film/Documentary Festival Subtitles — Broadcast Quality (any length)** — An independent filmmaker needs broadcast-quality subtitles for festival submission: specific formatting requirements, reading speed compliance, and professional styling. NemoVideo: generates subtitles meeting broadcast standards (maximum 2 lines, maximum 42 characters per line, minimum 1 second display, reading speed of 15-17 characters per second), applies professional positioning (centered at bottom, proper line breaks at grammatical boundaries — not mid-phrase), handles timing for complex audio (overlapping dialogue, background music, sound effects), and exports in the specific formats required by festival platforms and broadcast networks (SRT, STL, EBU-TT, TTML). Festival-ready subtitles that meet the technical specifications professional distributors require.

4. **Educational Content Subtitles — Learning-Optimized Display (any length)** — An educational platform's video library needs subtitles optimized for learning: slower display speed for complex content, technical term highlighting, and multi-language versions for international students. NemoVideo: adjusts reading speed based on content complexity (slower for dense technical explanations, normal for conversational segments), optionally highlights key terms (displaying technical vocabulary in bold or a different color the first time it appears), creates synchronized subtitle files for the platform's LMS player (compatible with SCORM, Canvas, Moodle, Blackboard), generates accessibility-compliant versions (WCAG 2.1 AA: proper contrast ratios, sufficient display time, non-overlapping text), and produces student-facing language versions. Subtitles designed for comprehension, not just consumption.

5. **Social Media Batch Subtitling — Library-Wide Coverage (multiple videos)** — A brand or creator has 100+ existing videos without subtitles that need captioning for compliance, engagement, and accessibility. NemoVideo: batch-processes the entire library with consistent subtitle styling, auto-detects the spoken language of each video (handling multilingual libraries without manual tagging), applies the brand's subtitle design standard across all videos, generates both embedded and standalone subtitle files for each video, and produces a captioned library from an uncaptioned one in hours rather than weeks. The subtitle debt that most content creators carry — eliminated in one operation.

## How It Works

### Step 1 — Upload Video
Any video with speech content in any language. NemoVideo auto-detects language and speaker count.

### Step 2 — Configure Subtitle Style and Languages
Choose visual style, target languages, display parameters, and export formats.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-subtitle-generator",
    "prompt": "Generate professional subtitles for a 20-minute product demo video. Primary: English subtitles with word-level timing, clean sans-serif font, white text with semi-transparent dark background bar. Position: bottom-center, 2 lines max. Speaker differentiation: presenter (white) vs. customer questions (yellow). Translations: Spanish, French, German, Japanese — same visual style, timing adjusted per language. Export: embedded MP4 for each language at 16:9 + standalone SRT files for all 5 languages + one 9:16 version with TikTok-style animated English captions for social clips.",
    "source_language": "en",
    "style": {
      "font": "clean-sans-serif",
      "color": "#FFFFFF",
      "background": "semi-transparent-dark-bar",
      "position": "bottom-center",
      "max_lines": 2
    },
    "speakers": {
      "differentiate": true,
      "presenter": "#FFFFFF",
      "customer": "#FFD700"
    },
    "languages": ["en", "es", "fr", "de", "ja"],
    "timing": "word-level",
    "exports": {
      "embedded_16x9": ["en", "es", "fr", "de", "ja"],
      "srt_files": ["en", "es", "fr", "de", "ja"],
      "social_9x16": {"language": "en", "style": "tiktok-animated"}
    }
  }'
```

### Step 4 — Review Accuracy and Timing
Play each language version. Check: transcription accuracy (especially proper nouns, technical terms, and numbers), timing synchronization (no early or late subtitles), line breaks at natural grammatical points (not splitting phrases awkwardly), and translation quality (natural phrasing, not machine-stiff). Correct and re-render.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Subtitle generation requirements |
| `source_language` | string | | Source audio language (auto-detect if omitted) |
| `style` | object | | {font, color, background, position, max_lines, animation} |
| `speakers` | object | | {differentiate, colors_per_speaker} |
| `languages` | array | | Target translation languages |
| `timing` | string | | "word-level", "phrase-level", "sentence-level" |
| `reading_speed` | string | | "slow" (12 cps), "standard" (15 cps), "fast" (18 cps) |
| `broadcast_compliance` | boolean | | Apply broadcast subtitle standards |
| `accessibility` | string | | "wcag-aa", "wcag-aaa", "custom" |
| `exports` | object | | {embedded, srt_files, social} output configuration |
| `batch` | boolean | | Process multiple videos |

## Output Example

```json
{
  "job_id": "aisub-20260329-001",
  "status": "completed",
  "source_language": "en",
  "transcription_confidence": 0.984,
  "word_count": 2840,
  "speakers_detected": 2,
  "languages_generated": 5,
  "outputs": {
    "embedded": {
      "en": {"file": "demo-sub-en-16x9.mp4"},
      "es": {"file": "demo-sub-es-16x9.mp4"},
      "fr": {"file": "demo-sub-fr-16x9.mp4"},
      "de": {"file": "demo-sub-de-16x9.mp4"},
      "ja": {"file": "demo-sub-ja-16x9.mp4"}
    },
    "srt_files": ["demo-en.srt", "demo-es.srt", "demo-fr.srt", "demo-de.srt", "demo-ja.srt"],
    "social": {"file": "demo-tiktok-en-9x16.mp4", "style": "tiktok-animated"}
  }
}
```

## Tips

1. **98% accuracy is the professional quality threshold** — Below 95%, errors are frequent enough that viewers notice and lose trust. At 98%+, errors are rare enough that the subtitle feels professionally produced. The difference between 85% (platform auto) and 98% (NemoVideo) is the difference between distracting and invisible.
2. **Word-level timing creates the sync that holds attention** — Phrase-level subtitles (a full phrase appears at once) create a disconnect between what the viewer reads and what they hear. Word-level timing (each word appears as spoken) creates a synchronized experience where reading reinforces listening. The synchronization itself is engaging.
3. **Speaker color differentiation prevents multi-person confusion** — In content with 2+ speakers, same-color subtitles force the viewer to constantly determine who is speaking. Different colors per speaker (white for host, yellow for guest) create instant visual identification that the brain processes before conscious thought. Color is faster than labels.
4. **Translation timing must adjust, not just translate** — A 5-word English phrase might translate to an 8-word German phrase. If the subtitle display time stays the same, the German viewer cannot finish reading before it disappears. NemoVideo adjusts display duration per language to maintain comfortable reading speed regardless of translation length differences.
5. **Batch subtitling eliminates subtitle debt permanently** — Most creators and organizations carry a growing library of uncaptioned content. Each new video adds to the debt. Batch processing the entire existing library in one operation eliminates the backlog and establishes the baseline for captioning all future content.

## Output Formats

| Format | Type | Use Case |
|--------|------|----------|
| MP4 (embedded) | Video | Social platforms, website, messaging |
| SRT | Subtitle file | YouTube, Vimeo, most platforms |
| VTT | Subtitle file | Web players, HTML5 |
| TTML | Subtitle file | Broadcast, streaming services |
| STL | Subtitle file | European broadcast standard |

## Related Skills

- [ai-video-caption-generator](/skills/ai-video-caption-generator) — Full caption workflow
- [auto-caption-video](/skills/auto-caption-video) — Quick auto-captioning
- [ai-video-text-overlay](/skills/ai-video-text-overlay) — Custom text graphics
- [ai-video-highlight-maker](/skills/ai-video-highlight-maker) — Captioned highlight clips
