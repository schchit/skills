---
name: camera-yolo-operator
description: Operate a local laptop or notebook camera and run YOLO object detection on the same machine. Supports webcam snapshot capture, timed multi-frame capture, short YOLO runs, and saving annotated result images. Use when the user asks to call the notebook/laptop camera, capture a few photos from the built-in webcam, run YOLO on the local camera feed, test local vision capability, or package webcam + YOLO workflows into a reusable OpenClaw skill. Triggers include 摄像头, webcam, 笔记本摄像头, YOLO, 目标检测, 抓拍, and camera-yolo tasks.
---

# Camera YOLO Operator

Use this skill for **local Windows webcam work** and **local YOLO detection** on the same Windows host where OpenClaw is installed.

## Platform baseline

Read `references/platform.md` before changing paths or assumptions.

This skill is written for the following tested platform:
- Windows 11
- NVIDIA GTX 1060 6GB
- OpenClaw installed directly on Windows
- Python 3.11 on Windows
- YOLO model stored in the workspace

## Quick workflow

1. Confirm the user wants the **local notebook/laptop camera**, not a paired mobile node camera.
2. For plain camera capture, run `scripts/capture_webcam_burst.py`.
3. For local detection, run `scripts/yolo_webcam_timed.py`.
4. Send the saved images back through the active messaging channel.
5. If the task is repeated, keep outputs under `workspace/tmp/` instead of scattering files.

## Camera capture

Use `scripts/capture_webcam_burst.py` when the user asks for:
- "拍几张笔记本摄像头照片"
- "抓几张本机摄像头图片"
- "测试一下摄像头"

### Command

```powershell
C:\Users\25697\AppData\Local\Programs\Python\Python311\python.exe scripts\capture_webcam_burst.py --count 3 --interval 0.4
```

### Behavior

- Open webcam index `0`
- Prefer DirectShow on Windows for stability
- Warm up several frames before saving
- Save multiple JPEG files into `workspace/tmp/camshots/`
- Print saved paths for follow-up sending

## YOLO timed detection

Use `scripts/yolo_webcam_timed.py` when the user asks for:
- "运行 30 秒 YOLO"
- "用摄像头跑目标检测"
- "把检测结果图发几张过来"

### Command

```powershell
C:\Users\25697\AppData\Local\Programs\Python\Python311\python.exe scripts\yolo_webcam_timed.py --seconds 30 --save-every 10 --max-saves 3
```

### Behavior

- Load the YOLO model from the configured workspace path
- Open local webcam index `0`
- Run inference on live frames for a fixed duration
- Save annotated frames periodically into `workspace/tmp/yolo-captures/`
- Print detected object labels and saved file paths

## Path rules

Default paths in this skill are intentionally explicit and Windows-specific. If the workspace moves, update:
- model path
- python path
- output path

Do not assume WSL paths for this skill.

## Troubleshooting

### Camera cannot open

Check:
- another app is not occupying the webcam
- webcam exists in Device Manager
- OpenCV can open index `0`

Fallback:
- retry with default backend if `cv2.CAP_DSHOW` fails

### YOLO import or model load fails

Check:
- `ultralytics`, `torch`, `opencv-python` are importable
- the model file exists
- the Python interpreter is the Windows Python, not WSL Python

### GPU not used

This skill can still run on CPU, but slower. Report the actual runtime state instead of guessing.

## Output guidance

When reporting back to the user:
- state whether the camera opened successfully
- state how many images were saved
- for YOLO runs, summarize detected labels briefly
- if only one image was produced, say so plainly

## Resources

### scripts/
- `capture_webcam_burst.py` — local webcam multi-shot capture on Windows
- `yolo_webcam_timed.py` — timed YOLO webcam detection with periodic annotated image saves

### references/
- `platform.md` — tested platform, assumptions, and maintenance notes
