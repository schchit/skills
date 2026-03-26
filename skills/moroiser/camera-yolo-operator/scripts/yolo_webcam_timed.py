import argparse
import os
import sys
import time

import cv2
import torch
from ultralytics import YOLO

DEFAULT_MODEL = r"C:\Users\25697\.openclaw\workspace\assets\yolo\yolo11s.pt"
DEFAULT_OUTPUT_DIR = r"C:\Users\25697\.openclaw\workspace\tmp\yolo-captures"


def open_camera(index: int):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if cap.isOpened():
        return cap
    cap.release()
    cap = cv2.VideoCapture(index)
    if cap.isOpened():
        return cap
    return cap


def main():
    parser = argparse.ArgumentParser(description="Run timed YOLO detection on the local Windows webcam.")
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--seconds", type=int, default=30)
    parser.add_argument("--save-every", type=float, default=10.0)
    parser.add_argument("--max-saves", type=int, default=3)
    parser.add_argument("--conf", type=float, default=0.5)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    if not os.path.exists(args.model):
        print(f"ERROR: model not found: {args.model}", file=sys.stderr)
        sys.exit(2)

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}")
    model = YOLO(args.model)

    cap = open_camera(args.camera_index)
    if not cap.isOpened():
        print("ERROR: camera open failed", file=sys.stderr)
        sys.exit(3)

    start = time.time()
    last_save_at = start
    save_count = 0
    labels = set()
    saved_paths = []

    while time.time() - start < args.seconds:
        ok, frame = cap.read()
        if not ok:
            break

        results = model(frame, conf=args.conf, verbose=False)
        annotated = results[0].plot()

        if results and results[0].boxes is not None and len(results[0].boxes) > 0:
            for cls in results[0].boxes.cls.cpu().numpy():
                labels.add(results[0].names[int(cls)])

        now = time.time()
        if save_count < args.max_saves and now - last_save_at >= args.save_every:
            save_count += 1
            path = os.path.join(args.output_dir, f"yolo_{save_count}.jpg")
            cv2.imwrite(path, annotated)
            saved_paths.append(path)
            print(f"Saved: {path}")
            last_save_at = now

    cap.release()

    print("Detected:", ", ".join(sorted(labels)) if labels else "none")
    for path in saved_paths:
        print(path)


if __name__ == "__main__":
    main()
