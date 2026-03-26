import argparse
import os
import sys
import time

import cv2


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
    parser = argparse.ArgumentParser(description="Capture multiple photos from the local Windows webcam.")
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--interval", type=float, default=0.4)
    parser.add_argument(
        "--output-dir",
        default=r"C:\Users\25697\.openclaw\workspace\tmp\camshots",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    cap = open_camera(args.camera_index)
    if not cap.isOpened():
        print("ERROR: camera open failed", file=sys.stderr)
        sys.exit(2)

    for _ in range(10):
        cap.read()
        time.sleep(0.08)

    saved = []
    for i in range(1, args.count + 1):
        ok, frame = cap.read()
        if not ok:
            print(f"ERROR: failed to read frame {i}", file=sys.stderr)
            cap.release()
            sys.exit(3)
        path = os.path.join(args.output_dir, f"shot{i}.jpg")
        if not cv2.imwrite(path, frame):
            print(f"ERROR: failed to write {path}", file=sys.stderr)
            cap.release()
            sys.exit(4)
        saved.append(path)
        time.sleep(args.interval)

    cap.release()
    for path in saved:
        print(path)


if __name__ == "__main__":
    main()
