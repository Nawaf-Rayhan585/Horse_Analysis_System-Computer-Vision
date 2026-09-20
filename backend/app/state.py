"""Thread-safe shared state between the video processing thread and the API."""
import threading
import time


class AppState:
    def __init__(self):
        self._lock = threading.Lock()
        self._frame_jpeg: bytes | None = None
        self._horses: list[dict] = []
        self._camera_status = "STARTING"
        self._camera_message = "Initializing camera feed..."
        self._processed_fps = 0.0

    def update_frame(self, jpeg_bytes: bytes):
        with self._lock:
            self._frame_jpeg = jpeg_bytes

    def get_frame(self):
        with self._lock:
            return self._frame_jpeg

    def update_horses(self, horses: list[dict]):
        with self._lock:
            self._horses = horses

    def get_horses(self):
        with self._lock:
            return list(self._horses)

    def set_camera_status(self, status: str, message: str = ""):
        with self._lock:
            self._camera_status = status
            self._camera_message = message

    def get_camera_status(self):
        with self._lock:
            return self._camera_status, self._camera_message

    def set_fps(self, fps: float):
        with self._lock:
            self._processed_fps = fps

    def get_fps(self):
        with self._lock:
            return self._processed_fps


app_state = AppState()
