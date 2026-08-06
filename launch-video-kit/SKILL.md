---
name: launch-video-kit
description: End-to-end product/demo/launch video as code (Remotion + AI voice + UI rebuilt in HTML/CSS). Covers discovery, concept, music, voice, subtitles, camera, render, and build-in-public content. Use when making any product video with AI, or adding voiceover, music, subtitles, or camera movement to a Remotion video.
---

# launch-video-kit

An agent skill for making product/demo/launch videos entirely in code — no video
editor. Remotion + AI voice + HTML/CSS UI reconstruction.

## Discovery

Before writing a single line, gather what you need from the user. If any of this
is already provided in context, skip those items. **Never guess — ask.**

Ask the user for:

1. **Topic + audience** — What's the video about? Who is it for? What should
   the viewer take away? If it's a product: what problem does it solve?
2. **Visual assets** — Screenshots, screen recordings, logo, brand colors,
   product URL. If not available, ask for a URL to capture from.
3. **Tone + style** — Minimal / energetic / playful / corporate? Reference
   videos? Color palette preference (monochrome + one accent, full brand,
   etc.)?
4. **Target platform + length** — Twitter/X, YouTube, LinkedIn, TikTok, etc.
   This affects aspect ratio (16:9, 9:16, 1:1) and ideal duration.

Collect all answers into a **brief** before proceeding.

## Concept

Once you have the discovery answers, establish the creative direction in a
**separate** conversation or model call — ask how to SELL the product, not
describe it.

Extract four decisions:
1. **Main message** = the closing line (what viewers should remember).
2. **One-line positioning** = the opening hook (what makes them keep watching).
3. **The demo** = what to show on screen (feature walkthrough, comparison,
   before/after, testimonial).
4. **Forbidden words/phrases** = things the brand avoids.

Write a brief that fixes **tone** and **what NOT to say**. Do NOT fix per-scene
seconds — decide those with the render in front.

## Roles

- **User = DIRECTOR** — decides on concept, style, pacing, final approval.
- **Agent = PRODUCER** — maintains a `VIDEO-CHECKLIST.md` with phases, a file
  map, and a todo. Proposes changes, executes the pipeline, measures results.

## Pipeline order

The order is critical. Follow it strictly.

### 1. Music first, story mapped to its arc (`analyze-music.mjs`)

Choose a music track, then map the story ONTO the music — not the reverse.

**What the script does:**
- Takes a music file (MP3/WAV).
- Computes per-segment RMS energy (e.g. per second or per beat).
- Prints an energy curve so you pick a **window** whose arc matches the video's
  narrative arc (build → climax → wind-down).
- Prints **beat/bar grid lines** in frames so cuts land on musical phrases.

**Rules:**
- The big drop MUST land on the key moment.
- Check the video is long enough to reach it — if the drop is at track-second X,
  the video must run ≥ X.
- Quiet sections → dense/reading scenes; drops → climactic reveals. Never the
  reverse.

**How to replicate without the script:**
```bash
# Energy analysis — per-second RMS:
ffmpeg -i track.mp3 -af "aresample=8000,ebur128=peak=false" -f null /dev/null

# Find silence gaps for splicing:
ffmpeg -i track.mp3 -af silencedetect=noise=-40dB:d=0.3 -f null /dev/null
```

### 2. Voice first, then edit (`gen-voice.mjs`)

Generate one WAV file **per line of narration** using a TTS engine (Kokoro,
Piper, or any local TTS that outputs raw PCM/WAV).

**What the script does:**
- Takes a text file with one narration line per row.
- Calls a local TTS binary/API for each line, producing `line_001.wav`,
  `line_002.wav`, etc.
- Normalizes to loudnorm `I=-16:TP=-1.5` and trims silences.
- Measures each WAV's exact duration in **frames** (at the project's target
  framerate, e.g. 30 fps).
- Prints a map of `lineIndex → frameCount` so the Remotion composition knows
  how long each scene must be.

**Why this goes second (not first):** Music arc was already chosen; voice
durations now fix the per-scene timing on top of that arc.

**How to replicate without the script:**
```bash
# Generate WAV with your TTS, then normalize + measure:
ffmpeg -i line_001.wav -af loudnorm=I=-16:TP=-1.5 -ar 44100 normalized.wav
ffprobe -v error -show_entries format=duration -of csv=p=0 normalized.wav
# seconds × framerate = frame count
```

### 3. Loop music to fit (`loop-music.mjs`)

Extend the chosen music window to match the video's total duration.

**What the script does:**
- Takes the chosen music window and the target duration.
- Finds **low-energy gaps** (near-silence) to splice in a loop point.
- Crossfades the splice and verifies the seam falls below a silence threshold.
- Outputs a single extended WAV/MP3 matching the video length.
- If no clean splice point exists, it reports the failure so you pick different
  gaps.

**How to replicate without the script:**
```bash
# Crossfade between two splice points:
ffmpeg -ss START -t FIRST_HALF -i track.mp3 \
       -ss SECOND_START -t SECOND_HALF -i track.mp3 \
       -filter_complex "[0][1]acrossfade=d=0.5:c1=tri:c2=tri[out]" \
       -map "[out]" looped.wav
```

### 4. Scaffold the Remotion project

**By hand** (deterministic; avoids `npx create-video` interactivity):

- `src/timing.ts` — the **single source of truth** for timing. Everything
  references this file.
- `Root.tsx` + `index.ts` — canonical pattern. **JSX only in `.tsx`!**
  (esbuild does not parse JSX in `.ts` files.)
- `src/audio.ts`, `src/Subtitle.tsx`, `src/camera.ts` — kit helpers.
- `public/` — assets, **ASCII-named only** (spaces and accents break
  `staticFile()`).

### 5. Reconstruct the product UI

Use a **vision-capable model** — a non-vision agent CANNOT see images/video.

Write a detailed prompt for the vision model:
- Style rules: monochrome + ONE accent color reserved for the climax.
- Demo data centralized in `theme.ts`.
- **Pixel-by-pixel color sampling** from real captures (never estimate by eye).
- The scene list from the brief.
- "Don't touch timing or composition."

Have it write components to `src/ui/` exporting a `SCENE_COMPONENTS` map
(`id → component`).

### 6. Wire it up

The composition consumes `SCENE_COMPONENTS` by scene id:
- Voice placed at exact frames (from the gen-voice map).
- Music with ducking — **`DUCK.base` must not exceed ~0.85.** Library tracks
  come at 0 dB; any effects on top will clip.
- Subtitles as a **separate-language layer** (e.g. EN voice + ES subtitles).
  Subtitle only what isn't already on screen as text. `dur` = reading time,
  not voice duration.
- Camera: **still, with short travels (~24 frames).** No continuous drift
  (distracts), no hard cuts (jarring). Each scene starts framed where the
  previous ended.

### 7. Render + measure

An agent can't see or hear the video. **Everything subjective has a
measurable proxy.**

```bash
# Contact sheet from numbered frame sequence (no glob in Git Bash):
ffmpeg -v error -i f_%d.png -vf "scale=560:-1,tile=5x4" -frames:v 1 sheet.png

# Voice-over-music mix check: voice level in mixed file ≈ voice alone
ffmpeg -hide_banner -ss 27 -t 4 -i out.mp4 -af volumedetect -f null /dev/null

# Global peak must stay below -1 dB
ffmpeg -hide_banner -i out.mp4 -af volumedetect -f null /dev/null
```

Iterate with the render in front. Fix visuals via the vision model.

## Content along the way

Each phase = one serialized post: *"día N — [phase]"*. Produce:
- Standalone tweets/posts per phase.
- A recap thread at the end.
- Fail in public — failed attempts ARE content.

Maintain a `posts.md` with ready-to-publish drafts.

## Rules that agents (and humans) easily skip

- **One voice file per line.** Never one long take.
- **Subtitle only what isn't already on screen.**
- **`DUCK.base` ≤ 0.85.**
- **Camera holds still, travels ~24 frames, no continuous drift.**
- **Same component on both sides of a seam** — if a scene is hand-painted it
  will differ in one detail, and that pops at the block boundary.
- **Iterate on timing, not content.** A loop over content that indexes a
  shorter timing array crashes the render as soon as you remove a beat.
- **Mounting before the voice** — real TTS durations shift every scene. Always
  voice-first.

## Environment

- **Required:** `ffmpeg` and `ffprobe` in PATH, Node 20+.
- **TTS:** Kokoro, Piper, or any local TTS binary that outputs WAV.
- **On Git Bash / Windows:** ffmpeg has no `glob` patterns (use numbered
  sequences), `drawtext` fails due to missing fontconfig (specify fonts by
  path), no `bc`.
- **Remotion quirks:** `staticFile()` breaks on spaces/accents — ASCII names
  only. `useVideoConfig().durationInFrames` inside a `<Sequence>` returns the
  sequence duration, not the video duration.

## What a TTS can't do

A TTS produces speech, not breath. Suspiros, laughs, and sound effects must be
recorded separately. Synthetic blips are possible via ffmpeg:
```bash
ffmpeg -f lavfi -i "sine=frequency=880:duration=0.15" -c:a pcm_s16le blip.wav
```

## Verification

1. `npx tsc --noEmit` is clean.
2. `npx remotion compositions` lists the composition with the right
   fps/size/duration.
3. A full render succeeds (e.g., `out/video.mp4`).
4. Contact sheet (numbered frames tiled) shows every scene, not black.
5. `ffmpeg volumedetect` on the render: global peak < −1 dB; voice-over-music
   segment mean ≈ voice-alone mean.
