# Platform Notes

## Tested environment

- OS: Windows 11
- GPU: NVIDIA GeForce GTX 1060 6GB
- OpenClaw install mode: installed directly on Windows
- Workspace: `C:\Users\25697\.openclaw\workspace`
- Python: `C:\Users\25697\AppData\Local\Programs\Python\Python311\python.exe`

## Model location

- YOLO model: `C:\Users\25697\.openclaw\workspace\assets\yolo\yolo11s.pt`

## Why this skill is Windows-specific

This skill is meant for the notebook's local webcam and a Windows-local Python environment.

It intentionally assumes:
- Windows paths
- direct access to local webcam hardware
- OpenCV camera backend behavior on Windows
- OpenClaw running on the same Windows host

## Maintenance notes

If the webcam index changes or multiple cameras appear, test camera indices manually.

If the GPU stack changes, verify:
- `torch.cuda.is_available()`
- model inference still works
- saved images still land under `workspace/tmp/`

## Suggested output folders

- Raw webcam captures: `workspace/tmp/camshots/`
- Annotated YOLO captures: `workspace/tmp/yolo-captures/`
