---
name: e-learning-video-maker
version: "1.0.0"
displayName: "E-Learning Video Maker — Create Online Course and E-Learning Module Videos for Educators and Course Creators"
description: >
  You recorded 8 hours of screen share with your voice-over for your online course on financial modeling, uploaded it to Teachable, and three months later you have a 2.1-star rating and twelve refund requests because students said the content was hard to follow. The problem isn't your expertise — it's that screen recordings with a talking head in the corner is not e-learning, it's surveillance footage. E-Learning Video Maker creates structured online course and training module videos for course creators, educators, and corporate trainers: applies instructional design principles to segment content into learnable chunks, adds animated concept illustrations, progress indicators, and knowledge check prompts at the right intervals, and exports SCORM-compatible modules and standard video files for every major LMS platform and course marketplace.
metadata: {"openclaw": {"emoji": "💻", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# E-Learning Video Maker — Turn Your Expertise Into Courses Students Complete

## Use Cases

1. **Online Course Module Production** — Solo course creators on Udemy, Skillshare, and Teachable competing against professionally produced courses. E-Learning Video Maker transforms your raw recordings into structured modules with animated concept visuals, chapter markers, and the production quality that earns five-star reviews and reduces refund rates.

2. **Corporate LMS Content** — L&D teams producing compliance training, onboarding modules, and skills development content for upload to Workday Learning, Cornerstone, or TalentLMS. Create SCORM-compatible video modules with embedded knowledge checks that meet corporate e-learning standards without a dedicated instructional design team.

3. **Coaching Program Video Curriculum** — Business coaches, life coaches, and skills trainers building video-based programs for membership sites and cohort courses. E-Learning Video Maker structures your coaching methodology into a sequenced video curriculum with worksheets and action prompts that deliver outcomes clients pay premium prices for.

4. **Academic Course Supplements** — University professors and K-12 educators creating flipped classroom video content, exam review modules, and supplementary concept explanation videos. Produce lecture content that students actually watch — with visual reinforcement and appropriate pacing — for your LMS course page.

## How It Works

Upload your raw recordings or slides and describe your learning objectives, and E-Learning Video Maker structures, animates, and exports a complete e-learning module ready for your course platform or LMS.

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill": "e-learning-video-maker", "input": {"course_topic": "financial modeling fundamentals", "module": "DCF valuation", "target_learner": "finance professionals", "lms": "teachable"}}'
```
