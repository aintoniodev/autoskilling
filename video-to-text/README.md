# video-to-text

Extract transcript text from videos (TikTok, YouTube, Instagram, X, any URL)
or local video files — fully local, no API keys.

**Engine**: `yt-dlp` (download) + `ffmpeg` (audio) + `faster-whisper` (STT).

## Install

Agent Plugins compatible client, or copy the skill directly:

```bash
cp -r video-to-text/skills/video-to-text ~/.pi/agent/skills/video-to-text
```

Dependencies (one-time, system or venv Python):

```bash
pip install yt-dlp faster-whisper "curl_cffi<0.16"
```

`ffmpeg` on PATH (or pass `--ffmpeg <path>`).

## Usage

```bash
python skills/video-to-text/scripts/vxtract.py https://vm.tiktok.com/XXXX --lang es --srt
python skills/video-to-text/scripts/vxtract.py https://youtu.be/XXXX --lang auto
python skills/video-to-text/scripts/vxtract.py clip.mp4 --lang es
```

Output: transcript to stdout + `<title>.txt` (or `.md` with `--md`, plus
`.srt` with `--srt`).

## Why faster-whisper and not canary/transcribe.cpp

Measured 2026-08-13: canary-180m-flash and canary-1b-flash (transcribe.cpp)
silently return EMPTY output for Spanish on many inputs (content-dependent
EOS collapse — same file: 5s ok, 6s empty, 8s ok, 9–11s empty). faster-whisper
`small` transcribed every test case correctly, es and en, CPU and CUDA.
