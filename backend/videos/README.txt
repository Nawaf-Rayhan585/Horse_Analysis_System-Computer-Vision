Place your demo CCTV video here with this exact name:

    backend/videos/<your_video>.mp4  (then set VIDEO_PATH in app/config.py)

Requirements:
- Any standard format OpenCV can read (.mp4 with H.264 is safest).
- A short clip (30-90 seconds) of a horse walking, ideally crossing in and
  out of the area you want marked as the "safe zone" — this is what
  triggers the intrusion alert during the demo.

If this file is missing, the dashboard will show a "NO SIGNAL" placeholder
with this same path, instead of crashing.
