---
name: language-learning-video
version: 1.0.5
displayName: "Language Learning Video Maker — Create Vocabulary and Grammar Lesson Videos"
description: >
    Language Learning Video Maker — Create Vocabulary and Grammar Lesson Videos. Works by connecting to the NemoVideo AI backend. Supports MP4, MOV, AVI, WebM, and MKV output formats. Automatic credential setup on first use — no manual configuration needed.
metadata: {"openclaw": {"emoji": "🗣️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---

# Language Learning Video Maker — Vocabulary and Grammar Lesson Videos

The flashcard app says you've "learned" 2,000 words in French but the waiter in Lyon just asked if you wanted still or sparkling water and your brain served up the word for "library" instead. Language learning content bridges the gap between memorization and comprehension — viewers need to hear native pronunciation at natural speed, see the written form alongside the phonetic breakdown, understand grammar rules through pattern recognition rather than abstract tables, and encounter vocabulary in context rather than isolation. This tool transforms lesson scripts, recorded dialogues, and pronunciation clips into structured language-learning videos — vocabulary cards with native-speaker audio, grammar-rule visualizations with color-coded sentence diagrams, dialogue scenarios with subtitle tracks in both languages, spaced-repetition review segments built into the video timeline, pronunciation comparison overlays (learner vs native), and cultural-context sidebars that explain why the textbook phrase will get you a polite smile but the colloquial version will get you an actual conversation. Built for language teachers building YouTube or Udemy course libraries, polyglot content creators producing "learn X in Y days" series, travel-prep channels teaching survival phrases, heritage-language schools producing distance-learning materials, and corporate L&D teams creating multilingual onboarding modules.

## Example Prompts

### 1. French Survival Phrases — Airport to Hotel
"Create a 6-minute French survival-phrases lesson for travelers. Scenario-based structure: Scene 1 — Airport Immigration: 'Bonjour, je suis en vacances' (Hello, I'm on holiday) — show the phrase written, phonetic in brackets — [bon-ZHOOR, zhuh swee on vah-KAHNS], native-speaker audio at natural speed, then slow repeat. Officer response: 'Combien de jours?' (How many days?) — learner response: 'Cinq jours' (Five days). Scene 2 — Taxi: 'Pouvez-vous m'emmener à l'hôtel...' (Can you take me to the hotel...) — pronunciation trap callout: 'The H in hôtel is silent. Saying "hoe-TELL" marks you as English-speaking instantly.' Scene 3 — Hotel check-in: 'J'ai une réservation au nom de...' (I have a reservation under the name of...). Cultural sidebar: 'Always say Bonjour before any request. Skipping it is considered rude — more rude than your accent will ever be.' Each phrase gets: written French → phonetic → slow audio → natural-speed audio → cultural note. Closing: rapid-fire quiz — phrase appears in English, 3-second pause for the learner to recall, then the French answer. Parisian café ambient soundtrack."

### 2. Mandarin Tones — The Four Tones Explained
"Build a 5-minute Mandarin tone tutorial for absolute beginners. Opening hook: 'The word "ma" means mother, hemp, horse, or scold — depending on how you say it. Tones aren't decoration. They're the entire meaning.' Tone chart displayed: Tone 1 (high flat: mā), Tone 2 (rising: má), Tone 3 (dip: mǎ), Tone 4 (falling: mà). Each tone gets a visual — pitch contour line animated as the speaker says it, with a musical-note comparison: 'Tone 1 = holding a note. Tone 2 = asking a question in English. Tone 3 = the "really?" dip. Tone 4 = a command.' Practice pairs: mā/mà (mother/scold) — slow, then natural speed. Common mistake segment: 'English speakers default to Tone 2 on everything because English uses rising intonation for questions. In Mandarin, rising tone on the wrong word changes your restaurant order from chicken to frog.' Ten-word tone drill with color-coded tone marks: red = Tone 1, blue = Tone 2, green = Tone 3, yellow = Tone 4. Closing quiz: audio plays, learner identifies the tone number. Clean, focused visual — white background, large text, no clutter."

### 3. Japanese Business Keigo — Polite vs Humble Forms
"Produce an 8-minute business Japanese lesson on keigo (polite language). Context card: 'Keigo isn't optional in Japanese business. Using casual form in a meeting is the equivalent of showing up in pajamas.' Three levels demonstrated with the same sentence ('to go'): casual = iku, polite = ikimasu, humble = mairimasu, honorific = irasshaimasu. Table on screen showing all four forms with color coding: casual (gray), polite (blue), humble (green), honorific (gold). Scenario 1 — Email opening: 'お世話になっております' (osewa ni natte orimasu) — breakdown: お世話 = care/assistance, に = particle, なって = becoming, おります = humble form of 'to be' — 'This phrase has no direct English translation. It roughly means: thank you for your ongoing relationship. You'll write it 50 times a day.' Scenario 2 — Meeting introduction: compare '私は田中です' (casual self-intro) with '田中と申します' (humble: I am called Tanaka) — 'In a business meeting, using です about yourself sounds like you're introducing your friend, not yourself.' Practice drill: given the casual form, produce the humble form in 3 seconds. Furigana above all kanji throughout. Office ambient audio — keyboard typing, polite murmuring."

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the language, topic, level, scenarios, and teaching approach |
| `duration` | string | | Target video length (e.g. "5 min", "6 min", "8 min") |
| `style` | string | | Visual style: "classroom", "travel-scenario", "business", "immersive", "quiz-drill" |
| `target_language` | string | | The language being taught (e.g. "French", "Mandarin", "Japanese") |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `phonetic` | boolean | | Show phonetic transcription alongside native script (default: true) |
| `native_audio` | boolean | | Include native-speaker pronunciation at natural and slow speed (default: true) |

## Workflow

1. **Describe** — Write the lesson with target phrases, grammar rules, scenarios, and cultural context
2. **Upload (optional)** — Add native-speaker recordings, dialogue clips, or scenario footage
3. **Generate** — AI assembles the lesson with vocabulary cards, pronunciation overlays, and quiz segments
4. **Review** — Preview the video, verify pronunciation-timing accuracy, adjust the quiz pacing
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "language-learning-video",
    "prompt": "Create a 6-minute French survival phrases lesson: airport immigration, taxi, hotel check-in scenarios. Written French + phonetic + slow audio + natural speed per phrase. Cultural sidebar on Bonjour etiquette. Closing rapid-fire recall quiz. Parisian café ambient",
    "duration": "6 min",
    "style": "travel-scenario",
    "target_language": "French",
    "phonetic": true,
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Provide both the phrase and its phonetic breakdown** — "'Bonjour' [bon-ZHOOR]" gives the AI exact text for the vocabulary card overlay. Without phonetics, non-Roman scripts become unreadable walls of characters for beginners.
2. **Include the cultural context, not just the translation** — "'Always say Bonjour before any request' is more valuable than the translation itself. The AI renders cultural notes as styled sidebar cards that distinguish etiquette from vocabulary.
3. **Structure around scenarios, not grammar tables** — "Airport → Taxi → Hotel" is a narrative learners follow; "Present tense conjugation table" is a reference they skim. The AI builds chapter markers around scenarios, creating a rewatchable journey.
4. **Add a recall quiz at the end** — "English phrase → 3-second pause → French answer" creates an active-learning segment. The AI generates a visual countdown timer during the pause, turning passive viewing into participatory practice.
5. **Specify natural speed AND slow speed** — "Native audio at natural speed, then slow repeat" gives learners both the target and the training wheels. The AI sequences both automatically with a visual speed indicator.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube language course module |
| MP4 9:16 | 1080p | TikTok / Instagram Reels phrase-of-the-day |
| MP4 1:1 | 1080p | Instagram feed vocabulary card |
| SRT | — | Dual-language subtitle track for immersion |

## Related Skills

- [english-learning-video](/skills/english-learning-video) — English-specific lessons for ESL learners
- [spanish-learning-video](/skills/spanish-learning-video) — Spanish-specific lessons and conversation practice
- [kids-education-video](/skills/kids-education-video) — Children's educational content and learning games
