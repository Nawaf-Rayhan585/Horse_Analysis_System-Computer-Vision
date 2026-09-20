"""Background thread: reads the CCTV video, runs detection/tracking, and
publishes annotated frames."""
import threading
import time

import cv2

from . import annotate, config
from .detector import HorseDetector
from .state import app_state


def _encode(frame):
    h, w = frame.shape[:2]
    if w > config.STREAM_MAX_WIDTH:
        scale = config.STREAM_MAX_WIDTH / w
        frame = cv2.resize(frame, (config.STREAM_MAX_WIDTH, int(h * scale)))
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, config.JPEG_QUALITY])
    return buf.tobytes() if ok else b""


class VideoProcessor(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.detector = HorseDetector()

    def _serve_offline(self, message_lines):
        frame = annotate.no_signal_frame(1280, 720, message_lines)
        app_state.update_frame(_encode(frame))
        while True:
            time.sleep(1)

    def run(self):
        if not config.VIDEO_PATH.exists():
            msg = f"Video file not found. Place your CCTV clip at: {config.VIDEO_PATH}"
            app_state.set_camera_status("OFFLINE", msg)
            self._serve_offline([
                ("NO SIGNAL", 1.3, annotate.RED),
                ("Demo video not found. Place your file at:", 0.6, annotate.WHITE),
                (str(config.VIDEO_PATH), 0.55, annotate.AMBER),
            ])
            return

        cap = cv2.VideoCapture(str(config.VIDEO_PATH))
        if not cap.isOpened():
            msg = f"Could not open video file at: {config.VIDEO_PATH}"
            app_state.set_camera_status("OFFLINE", msg)
            self._serve_offline([
                ("CAMERA ERROR", 1.2, annotate.RED),
                ("Could not open the video file.", 0.6, annotate.WHITE),
            ])
            return

        source_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        frame_interval = 1.0 / source_fps
        app_state.set_camera_status("ONLINE", "")

        fps_window_start = time.time()
        fps_frame_count = 0

        while True:
            loop_start = time.time()
            ok, frame = cap.read()
            if not ok:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.detector.reset()
                continue

            try:
                self._process_frame(frame)
            except Exception as exc:  # keep the feed alive even if a frame errors
                app_state.set_camera_status("ONLINE", f"Processing warning: {exc}")

            fps_frame_count += 1
            now = time.time()
            if now - fps_window_start >= 1.0:
                app_state.set_fps(fps_frame_count / (now - fps_window_start))
                fps_window_start = now
                fps_frame_count = 0

            elapsed = time.time() - loop_start
            remaining = frame_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)

    def _process_frame(self, frame):
        detections = self.detector.detect_and_track(frame)

        horses_state = []
        for det in detections:
            is_person = det.class_id == config.PERSON_CLASS_ID
            horses_state.append(
                {
                    "id": det.track_id,
                    "type": "person" if is_person else "horse",
                    "confidence": round(det.confidence, 2),
                    "bbox": [round(v, 1) for v in det.bbox],
                }
            )
            annotate.draw_bbox(
                frame,
                det.bbox,
                annotate.PERSON if is_person else annotate.ACCENT,
                f"{'Person' if is_person else 'Horse'} #{det.track_id}  {int(det.confidence * 100)}%",
            )

        app_state.update_horses(horses_state)
        annotate.draw_timestamp_burnin(frame)
        app_state.update_frame(_encode(frame))


processor = VideoProcessor()
