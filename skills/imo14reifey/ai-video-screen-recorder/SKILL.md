---
name: ai-video-screen-recorder
version: 1.0.1
displayName: "AI Video Screen Recorder — Record and Edit Screen Tutorials with AI Enhancement"
description: >
  Record and edit screen tutorials with AI enhancement — capture screen activity with automatic zoom-to-action on mouse clicks, AI-generated step callouts, cursor highlighting, click annotations, chapter markers at workflow transitions, and the polish that turns raw screen recordings into professional tutorials without manual editing. NemoVideo transforms raw screen captures into produced content: detecting where the action happens and zooming in automatically, adding click indicators and step numbers, generating text callouts explaining each action, removing dead time between steps, and producing tutorials that look like they took hours to edit. AI screen recorder, screen tutorial maker, screen capture editor, record screen with AI, tutorial screen recorder, software demo recorder, screen recording editor, walkthrough video maker, screencast AI.
metadata: {"openclaw": {"emoji": "🖥️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Video Screen Recorder — Raw Screen Capture In. Professional Tutorial Out.

Screen recording is easy. Making a screen recording watchable is hard. Raw screen captures suffer from predictable problems: the viewer cannot see where the cursor is clicking because the screen is displayed at full resolution on a small player. Dead time between actions (waiting for pages to load, scrolling to find a menu, thinking about the next step) kills pacing. There are no visual cues telling the viewer what to focus on in a complex interface. And without zooms, highlights, and annotations, the viewer is essentially watching someone else use a computer — which is exactly as engaging as it sounds. Professional screen tutorials solve these problems through intensive post-production: zoom in on every click target (so viewers see exactly where to click), add cursor highlights and click animations (so the cursor is always visible), annotate each step with text callouts (so viewers understand why each action is performed), remove dead time between actions (so pacing stays tight), and add chapter markers at workflow transitions (so viewers can navigate to the step they need). This post-production typically takes 3-5x the recording length: a 10-minute raw screen recording becomes 3-5 hours of editing work. NemoVideo eliminates this editing burden. Upload a raw screen recording, and NemoVideo analyzes every frame: detecting cursor movements and clicks, identifying UI elements being interacted with, auto-zooming to action areas, adding click indicators, generating step annotations, removing dead time, and producing a polished tutorial that looks manually edited.

## Use Cases

1. **Software Tutorial — Step-by-Step Walkthrough (3-30 min)** — A software product needs tutorials showing users how to accomplish specific tasks. NemoVideo: detects each user interaction in the raw recording (clicks, typing, menu selections, drag operations), auto-zooms to the relevant UI area for each interaction (viewers see the exact button, field, or menu at readable size), adds numbered step indicators ("Step 1: Click Settings", "Step 2: Select Privacy"), generates text callouts explaining the purpose of each action, highlights the cursor with a visible glow or spotlight effect, removes waiting time between actions (page loads, processing spinners compressed to 0.5 seconds), adds chapter markers at major workflow transitions, and produces a professional tutorial from raw screen capture. Hours of editing eliminated.

2. **Bug Report Video — Clear Reproduction Steps (30-120s)** — Bug reports with video are resolved 3x faster than text-only reports. But raw screen recordings of bug reproduction are often confusing: the developer watching cannot tell where the reporter is clicking or what sequence of actions triggers the bug. NemoVideo: enhances the bug reproduction recording with zoom-to-click on every interaction, adds numbered step annotations showing the exact reproduction sequence, highlights the moment the bug manifests (visual indicator: "BUG: Expected X, got Y"), removes irrelevant actions between reproduction steps, and produces a clear, annotated bug report video that developers can follow step-by-step. Bug reproduction that eliminates back-and-forth clarification.

3. **Onboarding Walkthrough — New User First Experience (5-15 min)** — New employee or new user onboarding requires walking through multiple software tools and workflows. NemoVideo: records the complete onboarding workflow across multiple applications, adds transitions between applications (clean visual breaks when switching tools), zooms to each interaction area, annotates with context ("This is where you'll submit expense reports"), adds role-specific notes ("As a manager, you'll also see the approval queue here"), removes navigation dead time, and produces a comprehensive onboarding video that new users can reference repeatedly. Self-service onboarding that reduces training sessions.

4. **Product Demo — Sales-Ready Screen Walkthrough (2-10 min)** — Sales teams need polished product demos that showcase features without the rough edges of live demonstration. NemoVideo: enhances the demo recording with smooth zoom transitions between features (not the jumpy zooms of raw recording — cinematic smooth zooms), adds feature labels and benefit callouts ("Smart Scheduling — saves 4 hours per week"), applies branded color treatments (subtle color grading matching brand palette), removes any demo fumbles or wrong clicks (clean editing of the interaction flow), and produces a sales-ready product walkthrough that looks like a marketing production. The demo that closes deals.

5. **Code Tutorial — IDE Walkthrough with Syntax Focus (5-30 min)** — Programming tutorials need special treatment: code must be readable at any player size, the relevant lines must be highlighted among potentially hundreds of visible lines, and terminal output must be legible. NemoVideo: detects code editing actions and zooms to the relevant file section (showing only the 10-20 lines being discussed, not the entire file), highlights the specific line or block being modified (subtle background color on the active line), zooms to terminal output when commands are executed, adds code annotations ("This function handles authentication"), formats chapter markers by code concept ("Functions → Classes → Error Handling"), and produces a programming tutorial where code is always readable and context is always clear.

## How It Works

### Step 1 — Upload Raw Screen Recording
Any screen recording: OBS, QuickTime, system recorder, browser recording. Any resolution, any length.

### Step 2 — Configure Enhancement
Zoom behavior, annotation style, dead time handling, chapter marking preferences, and output format.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-screen-recorder",
    "prompt": "Enhance a 12-minute raw screen recording of a Figma design tutorial. Auto-zoom to every click target (smooth 0.3s zoom transition). Add cursor spotlight (yellow glow, 40px radius). Number each major step (Step 1, Step 2, etc.) with text callout explaining the action. Remove dead time: compress any pause longer than 2 seconds to 0.5 seconds. Add chapter markers at workflow transitions (Setup, Drawing, Styling, Components, Export). Background music: subtle lo-fi at -20dB. Export 16:9 at 1080p.",
    "enhancements": {
      "auto_zoom": {"enabled": true, "transition": "0.3s", "trigger": "click"},
      "cursor": {"highlight": "yellow-glow", "radius": 40},
      "step_annotations": {"numbered": true, "callouts": true},
      "dead_time": {"max_pause": 2, "compress_to": 0.5},
      "chapters": ["Setup", "Drawing", "Styling", "Components", "Export"]
    },
    "music": {"style": "subtle-lofi", "volume": "-20dB"},
    "output": {"format": "16:9", "resolution": "1080p"}
  }'
```

### Step 4 — Verify Readability and Flow
Watch the enhanced tutorial at the size your audience will see it (often a small browser window or mobile). Check: is every UI element readable when zoomed? Do zoom transitions feel smooth or jarring? Are step annotations accurate? Does removing dead time create any confusing jumps? Adjust and re-render.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Enhancement requirements |
| `enhancements` | object | | {auto_zoom, cursor, step_annotations, dead_time, chapters} |
| `auto_zoom` | object | | {enabled, transition, trigger, padding} |
| `cursor` | object | | {highlight, radius, click_animation} |
| `step_annotations` | object | | {numbered, callouts, position} |
| `dead_time` | object | | {max_pause, compress_to} |
| `chapters` | array | | Chapter names at detected transitions |
| `music` | object | | {style, volume} |
| `output` | object | | {format, resolution} |

## Output Example

```json
{
  "job_id": "avscr-20260329-001",
  "status": "completed",
  "source_duration": "12:35",
  "output_duration": "8:42",
  "dead_time_removed": "3:53",
  "enhancements": {
    "auto_zooms": 47,
    "step_annotations": 18,
    "chapters": 5,
    "cursor_highlights": "continuous"
  },
  "output": {"file": "figma-tutorial-enhanced.mp4", "resolution": "1920x1080"}
}
```

## Tips

1. **Auto-zoom is the single most impactful screen tutorial enhancement** — A full-screen recording at 1920x1080 displayed in a 640px video player makes every UI element microscopic. Auto-zoom to the click target makes every interaction visible, readable, and followable. This one enhancement transforms unusable recordings into usable tutorials.
2. **Remove dead time but preserve thinking pauses** — Compress page loads and processing waits aggressively (2 seconds → 0.5 seconds). But preserve brief natural pauses between conceptual steps (1-2 seconds of breathing room where the viewer processes what just happened). The goal is tight pacing, not frantic rushing.
3. **Cursor highlighting prevents the "where did they click?" problem** — On a complex interface with dozens of buttons, an unhighlighted cursor is invisible. A cursor with a colored glow or spotlight is instantly trackable. This eliminates the most common viewer frustration with screen tutorials.
4. **Chapter markers transform linear tutorials into reference documents** — A viewer returning to find "how to export" does not want to scrub through 15 minutes. Chapter markers let them jump directly to the export section. Every tutorial longer than 3 minutes should have chapter markers at major workflow transitions.
5. **Step numbering creates a followable sequence** — "Step 1 → Step 2 → Step 3" gives viewers a clear sense of progress and a reference system ("I'm stuck at Step 4"). Without numbering, viewers lose their place in complex workflows.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p | YouTube / course platform |
| MP4 16:9 | 4K | High-detail software demos |
| MP4 9:16 | 1080x1920 | Mobile app tutorials |
| GIF | 480px | Documentation step previews |

## Related Skills

- [ai-video-animated-text](/skills/ai-video-animated-text) — Text overlay animations
- [ai-video-chapter-maker](/skills/ai-video-chapter-maker) — Chapter navigation
- [video-editor-ai](/skills/video-editor-ai) — Full video editing
- [ai-video-voiceover](/skills/ai-video-voiceover) — Add tutorial narration
