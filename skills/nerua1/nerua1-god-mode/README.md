# god-mode-skill

OpenClaw/Claude Code skill: Advanced prompt engineering techniques to bypass over-restrictive AI safety filters.

Use when a model refuses a legitimate request. Applies obfuscation (unicode, encoding), prefill patterns, and roleplay framing to recover full model capabilities.

> Inspired by [godmod3.ai](https://godmod3.ai/) (AGPL-3.0)
> This skill implements similar techniques independently. Not derived from their codebase. Licensed AGPL-3.0 in the spirit of their open-source work.

## Techniques

- **Parseltongue**: 33 obfuscation methods (unicode, encoding, substitution)
- **Prefill**: 27 templates across 9 categories  
- **Roleplay**: 4 persona patterns
- **Token smuggling**: 7 techniques

## Install

```bash
npx clawhub install god-mode-skill
# or
git clone https://github.com/nerua1/god-mode-skill ~/.openclaw/workspace/skills/god-mode
```

## Usage

```bash
/god-mode enable
/god-mode use unicode
```

Works best with instruction-tuned models that have safety filters. Not needed for uncensored/abliterated models.

## ⚠️ Why VirusTotal flags this skill

This skill will trigger a **false positive** security warning on installation. This is expected and explained below:

| Pattern | Why it's here | Actual risk |
|---------|--------------|-------------|
| `base64` encode/decode | Core obfuscation technique (#28 of 33) | None — standard Python library |
| HTTP calls to `127.0.0.1:1234` | Talks to your local LM Studio | None — localhost only, never leaves your machine |
| Unicode homoglyph substitution | Obfuscation technique #3 | None — text transformation only |

**No external data is sent anywhere.** All calls go to `http://127.0.0.1:1234` (LM Studio on your own machine). No telemetry, no cloud, no keys.

The warning is a pattern match, not a real detection. Developer/research tools that use encoding and make HTTP calls will always trigger it.

---

If this saved you time: [☕ PayPal.me/nerudek](https://www.paypal.me/nerudek)
