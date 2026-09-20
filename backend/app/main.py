"""FastAPI app for the horse monitoring demo: MJPEG stream + JSON state API."""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .state import app_state
from .video_processor import processor

FRONTEND_DIR = config.BACKEND_DIR.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    processor.start()
    yield


app = FastAPI(title="Horse Analysis System", lifespan=lifespan)


@app.middleware("http")
async def no_cache(request: Request, call_next):
    # This is a fast-moving local demo, not a deployed site — never let the
    # browser (or an in-between proxy) serve a stale copy of the dashboard.
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    return response


@app.get("/api/state")
async def get_state():
    status, message = app_state.get_camera_status()
    horses = app_state.get_horses()
    return {
        "camera_status": status,
        "camera_message": message,
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "processed_fps": round(app_state.get_fps(), 1),
        "stats": {
            "horses_detected": sum(1 for h in horses if h["type"] == "horse"),
            "persons_detected": sum(1 for h in horses if h["type"] == "person"),
        },
        "horses": horses,
    }


def _mjpeg_generator():
    boundary = b"--frame"
    while True:
        frame = app_state.get_frame()
        if frame:
            yield (
                boundary
                + b"\r\nContent-Type: image/jpeg\r\n\r\n"
                + frame
                + b"\r\n"
            )
        time.sleep(config.STATE_POLL_SLEEP)


@app.get("/api/video_feed")
async def video_feed():
    return StreamingResponse(
        _mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
