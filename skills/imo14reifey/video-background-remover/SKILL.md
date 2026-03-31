---
name: video-background-remover
version: "1.3.1"
displayName: "Video Background Remover — Remove and Replace Video Background with AI"
description: >
  Video Background Remover — Remove and Replace Video Background with AI.
  Green screen effects without the green screen. Video Background Remover uses AI segmentation to detect and isolate subjects in your footage — people, products, objects — and removes or replaces the background automatically. Upload your video and describe what you want: 'remove the background completely,' 'replace with a solid white background for product use,' or 'blur the background to keep focus on the subject.' The AI handles edge detection, motion tracking across frames, and clean compositing. Works for talking head videos, product demonstrations, remote work backgrounds, social media content, and any footage where background control matters. Combine with color grading and titles in the same session. Transparency export available for compositing workflows. Export as MP4. Supports mp4, mov, avi, webm, mkv.
  
  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM. Free trial available.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
license: MIT-0
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---