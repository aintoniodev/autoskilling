#!/usr/bin/env python3
"""vxtract — extract transcript text from videos (TikTok, YouTube, ...) or local files.

Fully local: yt-dlp (download) + ffmpeg (audio) + faster-whisper (STT).
No API keys, no cloud. Spanish, English, or auto-detected language.

Usage:
  python vxtract.py <url|video-file> [options]

Options:
  --lang LANG     es | en | auto        (default: auto)
  --model NAME    faster-whisper size   (default: small)
  --device DEV    auto | cuda | cpu     (default: auto)
  --out DIR       output directory for .txt/.md/.srt  (default: current dir)
  --srt           also write an .srt subtitle file with timestamps
  --md            write markdown output (title + url + transcript)
  --subs          fast path: try YouTube auto-subtitles first (no STT)
  --format FMT    yt-dlp format selector (default: bestaudio/best, or best for TikTok)
  --keep          keep downloaded media and wav in a temp dir
  --ffmpeg PATH   ffmpeg binary         (default: C:\\ffmpeg\\bin\\ffmpeg.exe on Windows, else ffmpeg)
  --tmp DIR       temp dir for media    (default: system temp)

Examples:
  python vxtract.py https://vm.tiktok.com/XXXX --lang es --srt
  python vxtract.py https://youtu.be/XXXX --lang auto
  python vxtract.py clip.mp4 --lang es
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_FFMPEG_WIN = r"C:\ffmpeg\bin\ffmpeg.exe"


def log(msg: str) -> None:
    print(f"[vxtract] {msg}", file=sys.stderr)


def is_url(s: str) -> bool:
    return re.match(r"^https?://", s.strip()) is not None


def site_of(url: str) -> str:
    m = re.search(r"https?://(?:www\.|vm\.|m\.)?([^/]+)", url)
    return m.group(1).lower() if m else ""


def find_ffmpeg(explicit: str | None) -> str:
    if explicit:
        return explicit
    if os.name == "nt" and Path(DEFAULT_FFMPEG_WIN).exists():
        return DEFAULT_FFMPEG_WIN
    return "ffmpeg"


def pick_format(url: str, explicit: str | None) -> str:
    """TikTok has no audio-only stream (AAC is muxed in the mp4): 'bestaudio'
    fails with 'Requested format is not available'. YouTube: audio-only is fine."""
    if explicit:
        return explicit
    return "best" if "tiktok" in site_of(url) else "bestaudio/best"


def pick_impersonate(url: str) -> str | None:
    """YouTube blocks plain requests (429) without browser impersonation;
    TikTok's webpage request FAILS with impersonation enabled."""
    s = site_of(url)
    if "youtube" in s or "youtu.be" in s:
        return "chrome"
    return None


def download_media(url: str, tmpdir: Path, fmt: str, imp: str | None) -> tuple[Path, str]:
    import yt_dlp

    outtmpl = str(tmpdir / "media.%(ext)s")
    opts: dict = {
        "format": fmt,
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
    }
    if imp:
        from yt_dlp.networking.impersonate import ImpersonateTarget

        opts["impersonate"] = ImpersonateTarget(client=imp)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
    except Exception as exc:
        log(f"download failed: {exc}")
        log(f"hint: try --format best (TikTok) or --format bestaudio/best (others)")
        sys.exit(2)
    if not path or not Path(path).exists():
        # ext may differ from the info ext (e.g. webm); find any media.* in tmpdir
        cands = sorted(tmpdir.glob("media.*"))
        if not cands:
            log("download finished but no media file found")
            sys.exit(2)
        path = str(cands[-1])
    title = str(info.get("title") or "video").strip()
    return Path(path), title


def to_wav(media: Path, wav: Path, ffmpeg: str) -> None:
    r = subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-i", str(media), "-vn", "-ar", "16000", "-ac", "1", str(wav)],
        capture_output=True,
    )
    if r.returncode != 0:
        log(f"ffmpeg audio extraction failed: {r.stderr.decode('utf-8', 'replace')[:400]}")
        sys.exit(2)


def sanitize(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "_", name).strip().strip(".")
    return name[:80] or "video"


def transcribe(wav: Path, lang: str, model_name: str, device: str, want_srt: bool):
    from faster_whisper import WhisperModel

    if device == "auto":
        device = "cuda"
        try:
            model = WhisperModel(model_name, device="cuda", compute_type="float16")
        except Exception as exc:
            log(f"CUDA unavailable ({exc}); falling back to CPU")
            device = "cpu"
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
    elif device == "cuda":
        model = WhisperModel(model_name, device="cuda", compute_type="float16")
    else:
        model = WhisperModel(model_name, device="cpu", compute_type="int8")

    lang_arg = None if lang == "auto" else lang
    # Silero VAD rejects music-heavy audio (songs, noisy clips): try VAD first,
    # retry without it when nothing survives the filter.
    def run(vad: bool):
        segs, info = model.transcribe(str(wav), language=lang_arg, vad_filter=vad)
        return list(segs), info

    segs, info = run(vad=True)
    if not segs:
        log("VAD filtered everything (music-heavy audio?); retrying without VAD")
        segs, info = run(vad=False)
    text = " ".join(s.text.strip() for s in segs)
    detected = info.language if info else None
    prob = info.language_probability if info else 0.0
    return text, detected, prob, (segs if want_srt else None)


def fmt_srt(segs) -> str:
    def ts(t: float) -> str:
        h, rem = divmod(int(t * 1000), 3600000)
        m, rem = divmod(rem, 60000)
        s, ms = divmod(rem, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    out = []
    for i, seg in enumerate(segs, 1):
        out.append(f"{i}\n{ts(seg.start)} --> {ts(seg.end)}\n{seg.text.strip()}\n")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Extract transcript text from videos (local, no cloud).")
    ap.add_argument("target", help="video URL or local file path")
    ap.add_argument("--lang", default="auto", choices=["auto", "es", "en", "de", "fr"])
    ap.add_argument("--model", default="small")
    ap.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    ap.add_argument("--out", default=".")
    ap.add_argument("--srt", action="store_true")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--subs", action="store_true", help="try platform subtitles first (YouTube only)")
    ap.add_argument("--format", default=None)
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--ffmpeg", default=None)
    ap.add_argument("--tmp", default=None)
    args = ap.parse_args(argv)

    ffmpeg = find_ffmpeg(args.ffmpeg)
    tmpdir = Path(args.tmp) if args.tmp else Path(tempfile.mkdtemp(prefix="vxtract_"))
    tmpdir.mkdir(parents=True, exist_ok=True)

    title = Path(args.target).stem
    try:
        if is_url(args.target):
            url = args.target.strip()
            log(f"downloading {url} ...")
            fmt = pick_format(url, args.format)
            media, title = download_media(url, tmpdir, fmt, pick_impersonate(url))
            log(f"got {media.name} ({media.stat().st_size // 1024} KB)")
        else:
            media = Path(args.target)
            if not media.exists():
                log(f"file not found: {media}")
                return 2
        wav = tmpdir / "audio.wav"
        log("extracting audio ...")
        to_wav(media, wav, ffmpeg)
        log(f"transcribing ({args.model}, {args.device}, lang={args.lang}) ...")
        text, detected, prob, segs = transcribe(wav, args.lang, args.model, args.device, args.srt)
        if not text.strip():
            log("no speech detected (empty transcript)")
            return 1
        log(f"detected language: {detected} (p={prob:.2f})")

        outdir = Path(args.out)
        outdir.mkdir(parents=True, exist_ok=True)
        base = sanitize(title)
        if args.md:
            out = outdir / f"{base}.md"
            out.write_text(f"# {title}\n\n> fuente: {args.target}\n> idioma: {detected}\n\n{text}\n", encoding="utf-8")
        else:
            out = outdir / f"{base}.txt"
            out.write_text(text + "\n", encoding="utf-8")
        if args.srt:
            (outdir / f"{base}.srt").write_text(fmt_srt(segs), encoding="utf-8")
        print(text)
        log(f"wrote {out}")
        if args.srt:
            log(f"wrote {outdir / (base + '.srt')}")
    finally:
        if not args.keep and tmpdir.name.startswith("vxtract_"):
            shutil.rmtree(tmpdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
