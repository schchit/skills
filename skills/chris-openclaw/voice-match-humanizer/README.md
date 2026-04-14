# Voice Match Humanizer

An OpenClaw skill that clones your writing voice from samples and applies it to any text.

Unlike generic humanizers that strip AI patterns and call it a day, this skill learns *your* specific writing fingerprint -- sentence structure, vocabulary, tone, quirks -- and uses it to transform AI-generated text so it sounds like you actually wrote it.

## What it does

- **Build voice profiles** from your writing samples (blog posts, emails, LinkedIn posts, newsletters, etc.)
- **Score text** for AI detection risk with a detailed breakdown across vocabulary, structure, tone, and mechanics
- **Rewrite AI-generated text** to match a saved voice profile
- **Manage multiple named profiles** for different contexts ("blog-voice", "linkedin-voice", "email-voice")

## How it works

1. Feed the skill 3-5 samples of your real writing
2. It analyzes your sentence patterns, word choices, tone, humor style, punctuation habits, and more
3. It saves a reusable voice profile you can apply to any future text
4. When you have AI-generated content, it rewrites it to match your profile

Profiles are saved as markdown files and persist across sessions. Create as many as you need for different writing contexts.

## Example usage

```
"Build a voice profile from my blog posts in ~/writing/blog/"

"Does this LinkedIn post sound like AI wrote it?"

"Rewrite this draft using my blog-voice profile"

"I need a new profile for my newsletter -- here are some past issues"
```

## Installation

```bash
openclaw skill install chris-openclaw/voice-match-humanizer
```

## Why not just use a regular humanizer?

Most humanizer skills treat "human" as one generic voice. They remove AI patterns, but the result still doesn't sound like *you*. A marketing director's emails don't sound like a developer's blog posts, and neither sounds like a founder's investor updates. This skill captures those differences.

## License

MIT
