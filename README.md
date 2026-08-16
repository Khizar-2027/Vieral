# Vieral

An AI-assisted auto-editor for YouTube Shorts / Instagram Reels. Upload your own raw footage, and Vieral automatically trims it, crops it to 9:16, cuts dead air, and burns in accurate captions — so you can focus on recording, not editing.

Built as a personal project to remove the manual-editing bottleneck of starting a content channel.

## What it does

- **Trim** — preview your uploaded clip in-browser and pick exact start/end points
- **Crop to 9:16** — auto-resize and center-crop for Shorts/Reels/TikTok format
- **Remove silence** — detects and cuts dead air using FFmpeg silence detection, with natural padding so pauses don't feel robotically cut
- **Auto-captions** — transcribes your own voice with a local Whisper model and burns in styled, readable captions (optional — can be toggled off per video)
- **Background processing** — edits run as background jobs; the UI polls for status so you're not stuck waiting on a blocked request

All processing (transcription, video editing) runs locally via FFmpeg and `faster-whisper` — no external API keys required.

## Tech stack

**Backend:** FastAPI, SQLAlchemy, SQLite, JWT auth
**Video/AI:** FFmpeg (trim, crop, silence detection, caption burning), faster-whisper (local speech-to-text)
**Frontend:** React (Vite), react-router-dom, axios

## How it works

1. Upload a raw video clip to a project
2. Preview it in-browser, optionally pick trim start/end points
3. Choose crop-to-vertical and/or remove-silence
4. Toggle captions on/off
5. Click **Apply Edits** — the pipeline runs trim → crop → silence-removal → captions in order, as a background job
6. Download the finished, edited video once processing completes

## Status

Core editing pipeline is complete and working end-to-end through the UI. Actively in development — next up: multi-clip support and a video-style analysis feature (point it at a reference video, get back a plain-language breakdown of its pacing/caption style).

## Setup

```bash
# Backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Requires FFmpeg installed and available on your system PATH.

**Note:** newer `bcrypt` versions break `passlib`'s version detection — `requirements.txt` pins `bcrypt==4.0.1` to avoid this.
