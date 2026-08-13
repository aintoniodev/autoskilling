---
name: video-to-text
description: >-
  Extract transcript text from videos — TikTok, YouTube, Instagram, X, any URL
  — or local video files, fully local with no API keys. EN: 'transcribe this
  video', 'extract text/subtitles from video', 'video to text'; ES: 'parsear
  texto de video', 'transcribir este video', 'sacar el texto/subtítulos de
  este TikTok'. Ships executable code in scripts/ (vxtract.py): yt-dlp
  download + ffmpeg audio extraction + faster-whisper transcription with
  Spanish/English/auto language and CPU or CUDA, output .txt/.md/.srt.
license: MIT
metadata:
  author: Antonio Gómez
  version: "1.0.0"
  verified: 2026-08-13
  engines: yt-dlp + ffmpeg + faster-whisper (NOT transcribe.cpp/canary)
---

# Video to Text (vxtract)

Turn any video URL (TikTok, YouTube, Instagram, X, 1000+ sites) or local video
file into a transcript. Fully local: nothing leaves the machine, no API keys,
no cloud quota.

## When to Use

- "Transcribe this video / sacar el texto de este video / parsear el texto de
  este TikTok" — with a URL or a local video file.
- Need the transcript of a tutorial, talk, or clip as `.txt`, `.md`, or
  `.srt` subtitles.
- Video has no available subtitles, or platform subtitles are wrong/missing.

Do NOT use transcribe.cpp / canary models for this: their Spanish path
silently returns empty output on many inputs (see Pitfalls). faster-whisper
is the verified engine.

## Procedure

1. One-time setup (deps must exist in the environment):
   ```bash
   pip install yt-dlp faster-whisper "curl_cffi<0.16"
   # ffmpeg on PATH, or pass --ffmpeg <path> (default C:\ffmpeg\bin\ffmpeg.exe on Windows)
   ```
   First run downloads the whisper model (~460 MB for `small`) into the HF
   cache; later runs reuse it.

2. Run:
   ```bash
   python scripts/vxtract.py <url|file> [--lang es|en|auto] [--device auto|cuda|cpu] [--srt]
   ```
   - `--lang es` for Spanish output, `en` for English, `auto` (default)
     detects the language.
   - `--device cuda` for GPU (RTX-class, ~3s for a 30s clip); CPU also works
     (~15s per 30s clip).
   - `--srt` writes an `.srt` subtitle file with timestamps; `--md` writes
     markdown (title + source + transcript).
   - Local files work too: `python scripts/vxtract.py clip.mp4 --lang es`.

3. Transcript goes to stdout and to `<out>/<video-title>.txt`.

## Engine choices (measured 2026-08-13)

| Engine | Spanish | Notes |
|---|---|---|
| faster-whisper `small` | ✅ verified | VAD + long-audio handled natively; CUDA float16 or CPU int8 |
| transcribe.cpp canary-180m-flash | ❌ empty output | emits EOS immediately on many Spanish-conditioned inputs (content-dependent: 5s ok, 6s empty, 8s ok, 9–11s empty) |
| transcribe.cpp canary-1b-flash | ⚠️ flaky | fixes some 180m cases, breaks others (TikTok+en → empty) |
| YouTube auto-subs (`--subs`) | fast path | zero compute, but timedtext endpoint 429s from some IPs; use as optional shortcut only |

## Pitfalls

- **TikTok has no audio-only stream** (AAC is muxed in the mp4). `bestaudio`
  fails with "Requested format is not available". The script auto-picks
  `best` for TikTok URLs.
- **Impersonation is site-dependent**: YouTube needs `--impersonate chrome`
  (else 429); TikTok's webpage request FAILS with impersonation. The script
  auto-toggles per site. `curl_cffi` must be ≤0.15.x — yt-dlp rejects 0.16+
  and silently disables impersonation (YouTube starts 429ing).
- TikTok rate-limits after several rapid downloads from one IP ("Unexpected
  response from webpage request") — wait ~30s–1 min between runs.
- Empty transcript + exit 1 means no speech detected (VAD found nothing) —
  check the audio actually has voice (`ffmpeg -i x.wav -af volumedetect -f
  null -`).
- Do not run `--impersonate` and TikTok in the same invocation; do not pass
  `-f bestaudio` to TikTok manually.

## Verification

1. `python scripts/vxtract.py <tiktok-url> --lang es` prints a Spanish transcript.
2. `python scripts/vxtract.py <youtube-url> --lang auto` prints a transcript and the detected language.
3. `python scripts/vxtract.py clip.mp4 --srt` writes `<name>.srt` with timestamps.
4. GPU: `--device cuda` loads the model in ~2s and transcribes a 30s clip in ~3s.
