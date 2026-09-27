# 🐎 Horse Analysis System

Real-time horse and person tracking from a CCTV feed, with a live web dashboard.
Built with YOLOv8 + ByteTrack on a FastAPI backend.

<img width="1919" height="1079" alt="Horse Analysis System dashboard" src="https://github.com/user-attachments/assets/c2a17c24-ed34-44c2-aca8-f3e7325ad821" />

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![YOLOv8](https://img.shields.io/badge/YOLO-v8-purple.svg)

## Features

- Detects and tracks **horses** and **people** frame by frame (COCO YOLOv8n)
- **Stable IDs** — ByteTrack plus a custom ID-reuse step, so a horse that disappears for a few seconds comes back with the same ID
- Weak detections still feed the tracker but aren't drawn, so fewer ghost boxes
- Live **MJPEG video stream** in the browser with a CCTV-style timestamp burn-in
- Dashboard cards: horses detected, people detected, processing FPS, camera status
- Shows a "NO SIGNAL" screen instead of crashing if the video is missing

## How it works

```
video file ─► YOLOv8 (horse + person) ─► ByteTrack + stable IDs ─► annotated frame
                                                                  │
                        FastAPI  /api/video_feed (MJPEG)  ◄───────┤
                                 /api/state (JSON stats)  ◄───────┘
                                          │
                               frontend/ (HTML + JS dashboard)
```

## Project structure

```
backend/
  app/
    main.py             # FastAPI app: stream + state API, serves the frontend
    video_processor.py  # reads the video, runs detection, pushes frames
    detector.py         # YOLO + ByteTrack + stable ID logic
    annotate.py         # boxes, labels, timestamp overlay
    state.py            # thread-safe shared state
    config.py           # all settings in one place
  bytetrack_stable.yaml
  requirements.txt
  run.ps1               # Windows start script
  videos/               # put your demo video here
frontend/
  index.html  app.js  style.css
```

## Getting started

```bash
git clone https://github.com/Nawaf-Rayhan585/Horse_Analysis_System-Computer-Vision.git
cd Horse_Analysis_System-Computer-Vision/backend

python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

1. Put a video of horses in `backend/videos/`.
2. Set `VIDEO_PATH` in `backend/app/config.py` to that file name.
3. Start the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
# or on Windows: .\run.ps1
```

4. Open **http://localhost:8000**

`yolov8n.pt` downloads automatically on first run.

## Config

All tuning lives in `backend/app/config.py`:

| Setting | Default | What it does |
|---|---|---|
| `CONFIDENCE_THRESHOLD` | 0.2 | Min confidence fed to the tracker |
| `DISPLAY_MIN_CONFIDENCE` | 0.45 | Min confidence to draw a box |
| `NMS_IOU` | 0.45 | Overlap suppression (fewer duplicate boxes) |
| `ID_REUSE_SECONDS` | 8.0 | How long a lost ID can come back |
| `INFERENCE_IMGSZ` | 640 | YOLO input size |
| `STREAM_MAX_WIDTH` | 960 | Width of the browser stream |

## API

| Endpoint | Returns |
|---|---|
| `GET /api/state` | JSON: camera status, FPS, counts, tracked objects |
| `GET /api/video_feed` | Live MJPEG stream |

## Roadmap

- [ ] Safe-zone intrusion alerts
- [ ] Per-horse activity stats (walking / standing / lying)
- [ ] RTSP camera input

## License

MIT — see [LICENSE](LICENSE).

## Contact

Built by **Nawaf Rayhan** — [fayaz7rg@gmail.com](mailto:fayaz7rg@gmail.com) · [Portfolio](https://nawaf585.netlify.app)

If this helped you, drop a ⭐
