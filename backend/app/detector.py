"""YOLOv8 horse detection + ByteTrack multi-object tracking."""
import time
from dataclasses import dataclass

from ultralytics import YOLO

from . import config


@dataclass
class Detection:
    track_id: int
    class_id: int
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2) in pixel coords


def _iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


class HorseDetector:
    def __init__(self):
        self.model = YOLO(str(config.MODEL_PATH))
        # Stable-ID layer: maps the tracker's raw IDs to IDs that survive tracker resets.
        self._alias: dict[int, int] = {}
        self._known: dict[int, dict] = {}  # stable_id -> {cls, bbox, seen}
        self._next_id = 0

    def reset(self):
        """Forget all tracks/IDs (call when the video loops back to the start)."""
        self._alias.clear()
        self._known.clear()
        self._next_id = 0
        predictor = getattr(self.model, "predictor", None)
        for tracker in getattr(predictor, "trackers", None) or []:
            tracker.reset()

    def _stable_id(self, raw_id, class_id, bbox, active, now):
        sid = self._alias.get(raw_id)
        if sid in active:  # another track already claimed this ID this frame
            sid = None
        if sid is None:
            best, best_iou = None, 0.1
            for cand, info in self._known.items():
                if cand in active or info["cls"] != class_id:
                    continue
                if now - info["seen"] > config.ID_REUSE_SECONDS:
                    continue
                iou = _iou(bbox, info["bbox"])
                if iou > best_iou:
                    best, best_iou = cand, iou
            if best is None:
                self._next_id += 1
                best = self._next_id
            sid = best
            self._alias[raw_id] = sid
        self._known[sid] = {"cls": class_id, "bbox": bbox, "seen": now}
        return sid

    def detect_and_track(self, frame):
        results = self.model.track(
            frame,
            classes=[config.HORSE_CLASS_ID, config.PERSON_CLASS_ID],
            conf=config.CONFIDENCE_THRESHOLD,
            imgsz=config.INFERENCE_IMGSZ,
            iou=config.NMS_IOU,
            tracker=config.TRACKER_CFG,
            persist=True,
            verbose=False,
        )

        detections = []
        if not results:
            return detections

        boxes = results[0].boxes
        if boxes is None or boxes.id is None:
            return detections

        ids = boxes.id.int().tolist()
        confs = boxes.conf.tolist()
        xyxy = boxes.xyxy.tolist()
        cls = boxes.cls.int().tolist()

        now = time.time()
        active: set[int] = set()
        # Strongest first; drop weak boxes and duplicate tracks piled on the same object.
        order = sorted(range(len(ids)), key=lambda i: -confs[i])
        kept = []
        for i in order:
            if confs[i] < config.DISPLAY_MIN_CONFIDENCE:
                continue
            if any(cls[j] == cls[i] and _iou(xyxy[i], xyxy[j]) > 0.55 for j in kept):
                continue
            kept.append(i)

        # Tracks that already have an ID claim it first; new tracks may then reuse lost IDs.
        kept.sort(key=lambda i: ids[i] not in self._alias)
        for i in kept:
            track_id, confidence, box, class_id = ids[i], confs[i], xyxy[i], cls[i]
            sid = self._stable_id(int(track_id), int(class_id), tuple(box), active, now)
            active.add(sid)
            detections.append(
                Detection(
                    track_id=sid,
                    class_id=int(class_id),
                    confidence=float(confidence),
                    bbox=tuple(box),
                )
            )
        return detections
