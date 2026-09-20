"""Central configuration for the horse monitoring demo."""
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
VIDEO_PATH = BACKEND_DIR / "videos" / "19810456-uhd_3840_2160_24fps.mp4"

MODEL_PATH = BACKEND_DIR / "yolov8n.pt"
HORSE_CLASS_ID = 17  # COCO class index for "horse"
PERSON_CLASS_ID = 0  # COCO class index for "person"
CONFIDENCE_THRESHOLD = 0.2  # low on purpose: ByteTrack uses weak boxes to keep tracks alive
INFERENCE_IMGSZ = 640
TRACKER_CFG = str(BACKEND_DIR / "bytetrack_stable.yaml")
DISPLAY_MIN_CONFIDENCE = 0.45  # weak boxes still feed the tracker but are not shown
NMS_IOU = 0.45  # stricter overlap suppression -> fewer duplicate ghost boxes on one horse
ID_REUSE_SECONDS = 8.0  # a lost object reappearing this soon, nearby, keeps its old ID

# Streaming / performance
STREAM_MAX_WIDTH = 960
JPEG_QUALITY = 82
STATE_POLL_SLEEP = 0.03  # seconds between MJPEG frame pushes when idle
