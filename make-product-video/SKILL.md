---
name: "make-product-video"
description: "End-to-end product/demo launch video \"as code\" (Remotion + AI voice + UI rebuilt in HTML/CSS), built in public with content per step. Use when making any product video with AI, any topic."
version: 1
created: "2026-08-04"
updated: "2026-08-04"
---
## When to Use
When the user wants to create a product/demo/launch video using the "video is code" approach (Remotion + AI voice + reconstructed UI, no video editor), especially documenting the process as social content (build in public). Works for any product/topic. Triggers: "product video", "launch video", "demo video", "vídeo de producto", "make a video with AI", "video as code", "Remotion video", "anunciar una feature con vídeo".

## Procedure
1. Establish roles + a single source of truth: the user is the DIRECTOR (decides); the agent is the PRODUCER (maintains a VIDEO-CHECKLIST.md with phases + a file map + a todo, proposes changes, executes the pipeline). Source philosophy: Borja Perez, 'El vídeo es código' (X @borjaperfra); kit: github.com/borjaperfra/launch-video-kit.
2. Concept conversation in a SEPARATE chat/LLM: ask how to SELL the product, not describe it. Extract 4 decisions: (1) main message = closing line, (2) one-line positioning = opening hook, (3) the demo (what to show), (4) forbidden words. Write a brief that fixes tone + what NOT to say; do NOT fix per-scene seconds (decide those with the render in front).
3. Music first, story mapped to its arc: analyze the track (BPM, energy per second, drops) and map the story ONTO the arc — drop → climax, quiet section → dense/reading scene — not the reverse. The big drop MUST land on the key moment; check the video is long enough to reach it (if the drop is at track-second X, the video must run ≥ X).
4. Voice FIRST — its real durations fix scene timing: one WAV per line, normalized (loudnorm I=-16:TP=-1.5), silences trimmed; print an id/dur/frames table. NEVER mount before the voice. For local generation see the 'kokoro-local-tts' skill.
5. Scaffold the Remotion project BY HAND (deterministic; avoids npx create-video interactivity): src/timing.ts as the SINGLE source of timing, Root.tsx + index.ts canonical pattern (JSX only in .tsx!), copy the kit helpers (audio.ts, Subtitle.tsx, camera.ts), assets ASCII-named in public/.
6. Reconstruct the product UI in HTML/CSS via a VISION-capable model — a non-vision agent CANNOT see images/video. Write a detailed prompt: style rules (monochrome + ONE accent color reserved for the climax), demo data centralized in theme.ts, pixel-by-pixel color sampling from real captures, the scene list, 'don't touch timing/composition'. Have it write components to src/ui/ exporting a SCENE_COMPONENTS (id→component) map.
7. Wire it up: the composition consumes SCENE_COMPONENTS by scene id; voice placed at exact frames; music with ducking (base ≤ 0.85); subtitles as a SEPARATE-language layer (e.g., EN voice + ES subtitles). Camera holds still and travels only ~24 frames before the next framing; each scene starts where the previous ended (no visible cuts).
8. Render + MEASURE (the ritual — an agent can't see/hear the video, only measure it): contact sheet from a NUMBERED frame sequence (no glob in Git Bash), volumedetect (voice-over-music mean ≈ voice-alone mean; global peak < −1 dB). Iterate with the render in front; fix visuals via the vision model.
9. Content along the way: each phase = one serialized post ('día N —'); standalone tweets per phase + a recap thread at the end; fail in public (the failed attempts ARE content). Maintain a posts.md with ready-to-publish drafts.

## Pitfalls
- Mounting before the voice: real TTS durations shift every scene → redo. Always voice-first.
- Estimating colors by eye: sample pixel-by-pixel from real captures (write a small sampling script).
- npx create-video is interactive/slow and pulls a template you may not want; hand-scaffold the Remotion project.
- esbuild parses JSX ONLY in .tsx files — never put <Composition> JSX in index.ts (use Root.tsx).
- A non-vision agent cannot verify visuals: delegate UI build + visual fixes to a vision-capable model, and verify by render + contact sheet + measurements — never by guessing coordinates blind.
- staticFile() dislikes spaces/accents — ASCII asset names only.
- Git Bash on Windows: ffmpeg has no glob patterns (use numbered sequences), drawtext needs fontconfig, there is no bc.
- Camera that moves continuously reads as handheld; hard cuts read as jumps. Hold still, travel ~24 frames before the next framing.
- Subtitling a line that's already a full-screen rótulo duplicates text — UNLESS it's a different language (then it's the accessible subtitle layer, not a duplicate).
- The big music drop landing past the end of the video: if the video is too short, the climax falls on a weak mini-drop. Lengthen the video (within the brief's range) so the drop hits the hero moment.

## Verification
1. npx tsc --noEmit is clean.
2. npx remotion compositions lists the composition with the right fps/size/duration.
3. A full render succeeds (e.g., out/video.mp4).
4. Contact sheet (numbered frames tiled) shows every scene, not black.
5. ffmpeg volumedetect on the render: global peak < −1 dB; voice-over-music segment mean ≈ voice-alone mean (ducking is sufficient).