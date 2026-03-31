---
name: lecture-video-editor
version: "1.1.1"
displayName: "Lecture Video Editor — Edit and Enhance Academic Lectures and Educational Recordings"
description: >
  Edit and enhance academic lectures, classroom recordings, and educational presentations with AI — transform raw lecture captures into structured learning content with slide synchronization, speaker tracking, chapter navigation, key concept highlighting, searchable transcripts, Q&A segment extraction, and multi-format export for LMS platforms. NemoVideo handles the unique challenges of lecture video: synchronize slides with the speaker's verbal references, zoom between speaker and slide content based on what is most relevant at each moment, add topic headers and concept labels, create timestamp-based chapter navigation for non-linear study, generate searchable closed captions for review, extract key moments as standalone concept clips, and produce content optimized for Moodle Canvas Blackboard YouTube and self-paced study. Lecture video editor AI, academic video editor, classroom recording editor, educational video enhancer, lecture capture tool, course video editor, presentation recording editor, e-learning video maker, academic content creator.
metadata: {"openclaw": {"emoji": "🎓", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# Lecture Video Editor — From Raw Classroom Capture to World-Class Online Learning

Every university, training organization, and online educator faces the same problem: lecture recordings are essential for modern education but unwatchable in their raw form. A fixed camera at the back of a 200-seat lecture hall captures: a distant figure at a podium (too small to read facial expressions), slides projected on a screen (too small to read text at recording resolution), audio that bounces off walls (echo, HVAC noise, coughing students), 75 minutes of continuous footage with no chapter breaks (students cannot find the specific concept they need to review), and zero visual variety (the same wide shot for the entire lecture). Students need these recordings — 87% of students report using lecture recordings for exam review. But they need them in a form that actually supports learning: close-ups of the speaker when they are explaining (facial expression aids comprehension), clear slides when they are presenting (readable text and diagrams), chapter navigation (jumping to "Mitosis" rather than scrubbing through 75 minutes), concept labels (knowing what topic is being discussed at each moment), and searchable transcripts (finding the exact moment the professor explained the confusing concept). NemoVideo transforms raw lecture captures into structured educational video. The AI analyzes the lecture content — detecting slide changes, tracking the speaker, identifying topic transitions, and recognizing key concept moments — then produces an enhanced lecture video with intelligent camera switching, readable slides, chapter navigation, concept overlays, and searchable captions.

## Use Cases

1. **Large Lecture Enhancement — Back-of-Room Camera to Multi-View (45-90 min)** — A single camera at the back of a 300-seat lecture hall. Raw footage: the professor is 50 pixels tall, the projected slide is barely legible, and the audio has room echo. NemoVideo: creates an intelligent multi-view edit from the single camera — zooming to speaker close-up when they are explaining concepts verbally (face visible, gestures captured), zooming to slide content when they advance to a new slide (slide fills the frame, text becomes readable), using picture-in-picture when both speaker and slide are relevant (speaker small in corner, slide full-frame), cutting between views with smooth transitions timed to the lecture's natural rhythm. Adds noise reduction for echo, amplifies the speaker's voice above ambient noise, and produces a viewing experience that feels like sitting in the front row rather than watching from the back wall.

2. **Slide Synchronization — Presentation Recording with Perfect Timing (any length)** — A professor uses 60 slides in a 50-minute lecture. The raw recording shows the projected screen, but slide transitions are hard to detect (the projector is dim, the camera auto-adjusts exposure at each transition). NemoVideo: detects every slide change through visual analysis (frame differencing identifies the exact transition moment), captures a clean version of each slide (de-warping projection distortion, correcting keystoning, enhancing contrast for readability), displays the clean slide version alongside or alternating with the speaker video, and creates chapter markers at each major slide transition with the slide's topic as the chapter title. Students can navigate to any slide's discussion instantly.

3. **Topic Chapter Navigation — 75 Minutes to Searchable Segments (any length)** — A chemistry lecture covers: review of last week (5 min), new concept introduction (15 min), mathematical derivation (20 min), practical applications (15 min), example problems (15 min), Q&A (5 min). Without chapters, a student reviewing for the exam must scrub through the entire recording to find the derivation. NemoVideo: analyzes the lecture transcript for topic transitions (detecting when the professor says "Now let's move on to..." or "The next topic is..." or simply changes subject), creates chapter markers at each topic transition, labels chapters with descriptive topic names (not just "Chapter 3" but "Gibbs Free Energy Derivation"), and produces a navigable lecture where any concept is one click away. 75 minutes becomes 8-10 directly accessible topic segments.

4. **Concept Clip Extraction — Key Moments as Standalone Lessons (2-5 min each)** — Within a 60-minute lecture, there are 4-6 moments that are standalone-valuable: a particularly clear explanation of a difficult concept, a worked example that demonstrates a technique, an analogy that makes an abstract idea click. NemoVideo: identifies these high-value teaching moments through speech analysis (detecting explanation patterns, example patterns, and summary patterns), extracts each as a self-contained clip (with enough context before and after to stand alone), adds a concept title card ("Understanding Enzyme Kinetics — Key Concept"), adds the relevant slide as a visual reference, and produces a library of 2-5 minute concept clips. These clips become study resources, social content ("This professor explains entropy in 3 minutes"), and course marketing materials.

5. **Multi-Source Academic Recording — Camera + Screen Capture + Document Camera (any length)** — A modern lecture recording setup captures three sources simultaneously: room camera (showing the professor and the classroom), screen capture (the digital slides), and a document camera (hand-drawn diagrams, physical demonstrations). NemoVideo: synchronizes all three sources by timestamp, creates an intelligent edit that switches between sources based on relevance (screen capture when discussing slides, document camera when drawing diagrams, room camera when the professor is demonstrating physically), uses picture-in-picture when multiple sources are relevant simultaneously (document camera main view with speaker PiP during live diagramming), and produces a single cohesive video from three separate streams. Multi-source complexity becomes viewing simplicity.

## How It Works

### Step 1 — Upload Lecture Recording
Single camera capture, screen recording, document camera footage, or any combination. Raw, unedited recordings from any classroom setup.

### Step 2 — Define Enhancement Priorities
Slide sync, speaker tracking, chapter navigation, concept extraction, caption generation, or full enhancement (all of the above).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "lecture-video-editor",
    "prompt": "Enhance a 75-minute organic chemistry lecture from a single back-of-room camera. Speaker tracking: zoom to professor close-up during verbal explanations. Slide sync: detect all slide transitions, display clean de-warped slides at full readability when the professor references them. Multi-view switching: intelligent alternation between speaker, slide, and split-view. Noise reduction: remove room echo and HVAC hum. Chapter navigation: auto-detect topic transitions, create navigable chapters with descriptive labels. Concept clips: extract the 5 most standalone-valuable teaching moments as 2-4 minute clips with concept title cards. Closed captions: full transcript with speaker identification and chemical formula notation. Export 16:9 for Moodle LMS + concept clips at 9:16 for the department Instagram.",
    "source_type": "single-camera-back-of-room",
    "enhancements": {
      "speaker_tracking": true,
      "slide_sync": {"dewarp": true, "enhance_contrast": true},
      "multi_view": "intelligent-switching",
      "noise_reduction": {"echo": true, "hvac": true},
      "chapters": {"auto_detect": true, "descriptive_labels": true},
      "concept_clips": {"count": 5, "duration": "2-4 min", "title_cards": true},
      "captions": {"full_transcript": true, "formulas": true}
    },
    "formats": {"lecture": "16:9", "concept_clips": "9:16"}
  }'
```

### Step 4 — Review Academic Accuracy
Verify: slide text is readable, chapter labels accurately describe the content, concept clips are self-contained and correctly titled, captions correctly represent chemical formulas and technical terms. Adjust and re-render.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Lecture enhancement requirements |
| `source_type` | string | | "single-camera", "multi-source", "screen-recording", "hybrid" |
| `speaker_tracking` | boolean | | Zoom to speaker during verbal explanations |
| `slide_sync` | object | | {dewarp, enhance_contrast, clean_capture} |
| `multi_view` | string | | "intelligent-switching", "picture-in-picture", "side-by-side" |
| `noise_reduction` | object | | {echo, hvac, ambient, audience} |
| `chapters` | object | | {auto_detect, descriptive_labels, custom} |
| `concept_clips` | object | | {count, duration, title_cards} |
| `captions` | object | | {full_transcript, formulas, speaker_id, searchable} |
| `qa_extraction` | boolean | | Separate Q&A segment |
| `formats` | object | | {lecture, concept_clips} |

## Output Example

```json
{
  "job_id": "lected-20260329-001",
  "status": "completed",
  "source_duration": "75:12",
  "enhancements": {
    "view_switches": 47,
    "slides_detected": 42,
    "slides_dewarped": 42,
    "chapters_created": 9,
    "noise_reduction": "echo + HVAC removed",
    "concept_clips_extracted": 5,
    "caption_words": 11240
  },
  "outputs": {
    "enhanced_lecture": {"file": "orgchem-lec12-enhanced-16x9.mp4", "resolution": "1920x1080", "duration": "75:12"},
    "concept_clips": [
      {"file": "sn1-mechanism-9x16.mp4", "topic": "SN1 Reaction Mechanism", "duration": "3:12"},
      {"file": "stereochemistry-9x16.mp4", "topic": "Chirality and Stereoisomers", "duration": "2:48"},
      {"file": "nmr-basics-9x16.mp4", "topic": "Reading NMR Spectra", "duration": "3:45"},
      {"file": "retrosynthesis-9x16.mp4", "topic": "Retrosynthetic Analysis", "duration": "2:55"},
      {"file": "acid-base-9x16.mp4", "topic": "pKa and Acid Strength", "duration": "2:22"}
    ],
    "captions": {"file": "orgchem-lec12.vtt", "format": "WebVTT"}
  }
}
```

## Tips

1. **Intelligent view switching transforms a static recording into a directed learning experience** — A single camera recording forces the viewer to visually search the frame for relevant information. Automated switching between speaker close-up, slide display, and split-view directs attention exactly where learning happens at each moment.
2. **Slide de-warping is essential for readability** — Projected slides captured by a camera at an angle produce keystoning (trapezoid distortion) and low contrast. De-warping and enhancing these slides to readable quality is often the single most impactful improvement for lecture recordings.
3. **Chapter navigation respects how students actually use lecture recordings** — Students rarely watch lecture recordings linearly. They seek specific concepts for review, problem-solving, or exam preparation. Chapter navigation with descriptive topic labels converts a 75-minute recording from a time prison into a searchable reference library.
4. **Concept clips have value far beyond the course** — A 3-minute clip of a professor brilliantly explaining a difficult concept can reach millions on YouTube and TikTok. These extracted moments serve: exam review, social media for department visibility, prospective student marketing, and open educational resources. Always extract the best teaching moments.
5. **Searchable captions make lectures study-searchable** — A student who remembers the professor explaining something about "Gibbs free energy" but not when in the 75-minute lecture can search the caption transcript and jump directly to that moment. Searchable captions convert passive recordings into active study tools.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p | LMS (Moodle, Canvas, Blackboard) / YouTube |
| MP4 9:16 | 1080x1920 | TikTok / Reels (concept clips) |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |
| WebVTT / SRT | — | LMS caption integration |

## Related Skills

- [ai-video-caption-generator](/skills/ai-video-caption-generator) — Academic captions
- [ai-video-chapter-maker](/skills/ai-video-chapter-maker) — Auto chapter detection
- [ai-video-zoom](/skills/ai-video-zoom) — Zoom-to-detail on slides
- [ai-video-highlight-maker](/skills/ai-video-highlight-maker) — Key moment extraction
