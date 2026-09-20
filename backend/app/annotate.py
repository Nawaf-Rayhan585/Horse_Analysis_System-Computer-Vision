"""OpenCV drawing helpers for the CCTV-style overlay (boxes, timestamp, no-signal)."""
import time

import cv2
import numpy as np

# BGR colors (matched to the dashboard's warm accent palette)
ACCENT = (0, 140, 255)  # horse boxes (bright orange)
PERSON = (255, 200, 0)  # person boxes (bright cyan-blue)
RED = (52, 63, 161)  # muted brick, offline / error states
WHITE = (255, 255, 255)
BLACK = (18, 14, 10)
AMBER = (11, 158, 245)

FONT = cv2.FONT_HERSHEY_SIMPLEX


def _text_with_bg(frame, text, org, scale=0.55, color=WHITE, bg=BLACK, thickness=1, pad=4):
    (tw, th), baseline = cv2.getTextSize(text, FONT, scale, thickness)
    x, y = org
    cv2.rectangle(frame, (x - pad, y - th - pad), (x + tw + pad, y + baseline + pad), bg, -1)
    cv2.putText(frame, text, (x, y), FONT, scale, color, thickness, cv2.LINE_AA)


def draw_bbox(frame, bbox, color, label):
    x1, y1, x2, y2 = [int(v) for v in bbox]
    # Scale strokes with frame size so boxes stay bold after the 4K frame is downscaled.
    scale = max(1.0, frame.shape[1] / 960)
    line = max(4, int(3 * scale))
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, line, cv2.LINE_AA)

    corner = int(max(12, min(30, min(x2 - x1, y2 - y1) * 0.22)) * scale)
    thick = line * 2
    for cx, cy, dx, dy in (
        (x1, y1, 1, 1),
        (x2, y1, -1, 1),
        (x1, y2, 1, -1),
        (x2, y2, -1, -1),
    ):
        cv2.line(frame, (cx, cy), (cx + dx * corner, cy), color, thick, cv2.LINE_AA)
        cv2.line(frame, (cx, cy), (cx, cy + dy * corner), color, thick, cv2.LINE_AA)

    gap = int(8 * scale)
    label_y = y1 - gap if y1 - gap > int(15 * scale) else y2 + int(20 * scale)
    _text_with_bg(
        frame, label, (x1, label_y), scale=0.55 * scale, color=WHITE, bg=color,
        thickness=max(1, int(scale)), pad=int(4 * scale),
    )


def draw_timestamp_burnin(frame, camera_name="CAM-01 STABLE"):
    h, w = frame.shape[:2]
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    text = f"{camera_name}  |  {ts}"
    (tw, th), baseline = cv2.getTextSize(text, FONT, 0.5, 1)
    x, y = w - tw - 14, h - 14
    cv2.rectangle(frame, (x - 6, y - th - 6), (w - 6, y + baseline), (0, 0, 0), -1)
    cv2.putText(frame, text, (x, y), FONT, 0.5, (210, 210, 210), 1, cv2.LINE_AA)


def no_signal_frame(width, height, lines):
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (24, 18, 14)
    cv2.rectangle(frame, (0, 0), (width - 1, height - 1), (60, 50, 45), 2)

    y = height // 2 - (len(lines) * 32) // 2
    for i, (text, scale, color) in enumerate(lines):
        (tw, th), _ = cv2.getTextSize(text, FONT, scale, 2)
        x = (width - tw) // 2
        cv2.putText(frame, text, (x, y + i * 34), FONT, scale, color, 2, cv2.LINE_AA)
    return frame
