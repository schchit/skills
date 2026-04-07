---
name: yoga-studio-video
version: 1.0.0
displayName: Yoga Studio Video Maker
description: |
  Your yoga studio looks different on a Tuesday morning than it does in a photo — the light through the windows, students moving into poses, the instructor adjusting a shoulder. Yoga Studio Video captures that living atmosphere so people searching for their next class can feel what it's actually like to walk through your door.

  Make a promo video for a yoga studio, yoga class schedule video, hot yoga studio tour, beginner yoga class video, yoga teacher introduction, restorative yoga promo, prenatal yoga marketing video, or corporate yoga program explainer — and get something that brings in new students without a single cold call.

  **Use Cases**
  - New studio opening announcement with virtual tour
  - Instructor spotlight to introduce teachers and their specialties
  - Class schedule and pricing overview for website and Instagram
  - Corporate wellness yoga program pitch video

  **How It Works**
  Tell the AI your studio name, style (vinyasa, hatha, hot yoga, etc.), target student, and any key offers. It writes a complete promo script, generates a polished video with matching visuals and calm background music, ready to post.

  **Example**
  ```bash
  curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
    -H "Authorization: Bearer $NEMO_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "skill": "yoga-studio-video",
      "inputs": {
        "studio_name": "Sunrise Yoga",
        "style": "vinyasa and restorative",
        "target": "stressed professionals looking to unwind",
        "offer": "first class free"
      }
    }'
  ```
metadata:
  openclaw.emoji: "🧘"
  openclaw.requires: ["NEMO_TOKEN"]
  openclaw.primaryEnv: NEMO_TOKEN
  configPaths: ["~/.config/nemovideo/"]
---
# Yoga Studio Video

Capture the living atmosphere of your studio. This skill creates promo videos that help people searching for their next class feel what it is actually like to walk through your door.

## What It Does

- Studio tour and atmosphere video to introduce new students
- Instructor spotlight to showcase your teachers and their specialties
- Class schedule and pricing overview for website and social media
- Corporate wellness program pitch for B2B clients

## How to Use

Describe your studio name, yoga style (vinyasa, hatha, hot yoga, restorative), target student, and any special offers. The AI writes a complete promo script.

Example: Create a promo video for Sunrise Yoga, a vinyasa and restorative studio targeting stressed professionals. We offer a first class free trial.

## Tips

Show movement, not just poses. A 10-second clip of a class flowing in sync converts better than a static photo. Lead with the feeling, then the schedule.
