# linkedin-profile-archive

Archive a LinkedIn profile's **entire posting history** — text, images, and engagement
metrics — into a structured local folder for offline analysis. No premium API.

This is an **Agent Plugin** (Agent Plugins 1.0.0) that ships one skill
(`skills/linkedin-profile-archive/SKILL.md`) plus executable scripts.

## What it does

- Captures LinkedIn's internal `voyager/api` activity-feed request from a live,
  **logged-in** browser (Chrome/Brave) via CDP — no manual `curl` copying, no cookies
  stripped from the profile.
- Paginates through every post using the feed's `paginationToken` (the `start` offset
  alone returns the same first page every time).
- Extracts each post's text, URL, date, and like/comment/repost counts into
  `index.json` + one `posts/*.md` per post.
- Downloads each post's image **through the browser** (media.licdn.com 403s plain HTTP
  clients via Cloudflare TLS fingerprinting) with resume + reconnect.
- Summarizes cadence, top posts, engagement, and topics into a `REPORT.md`.

## Why the browser path

LinkedIn blocks plain HTTP scraping and encrypts session cookies with Chromium v20
"app-bound" protection, so they don't transfer to a copied profile and can't be replayed
by curl. The robust route is to drive the user's **real, currently logged-in** browser.

## Install

Copy this directory (plugin) anywhere, or copy just the skill:

```bash
cp -r skills/linkedin-profile-archive ~/.pi/agent/skills/linkedin-profile-archive
```

Prereqs:

```bash
pip install websocket-client requests
```

## Quick pipeline

```bash
# 1. start the logged-in browser with CDP on :9222 (your real profile dir)
brave --remote-debugging-port=9222 --user-data-dir="$HOME/AppData/Local/.../User Data"

# 2. capture the feed request
python skills/linkedin-profile-archive/scripts/capture_feed.py \
  --url "https://www.linkedin.com/in/<PUBID>/recent-activity/all/" --out session/capture

# 3. (edit session/capture/curl.txt to the count:20,start:0,profileUrn feed) then paginate
python skills/linkedin-profile-archive/scripts/fetch_all_pages.py \
  --endpoint session/capture/curl.txt --out session/pages

# 4. extract posts
python skills/linkedin-profile-archive/scripts/linkedin_archive.py \
  --raw session/pages --out output/<PUBID>

# 5. download images
python skills/linkedin-profile-archive/scripts/download_images.py \
  --images output/<PUBID>/images.json --dir output/<PUBID>/images

# 6. analyze
python skills/linkedin-profile-archive/scripts/linkedin_report.py \
  --index output/<PUBID>/index.json --md output/<PUBID>/REPORT.md
```

See `SKILL.md` for full detail and pitfalls.

## Components

| Script | Role |
|---|---|
| `capture_feed.py` | Navigate the activity page + capture voyager requests via CDP |
| `fetch_all_pages.py` | Paginate the feed with `paginationToken` until the last post |
| `linkedin_archive.py` | Extract posts (text/metrics/images manifest) from raw pages; `--curl` replay for replayable sessions |
| `download_images.py` | Binary-download post images through the browser (CDP) |
| `linkedin_report.py` | Cadence / top-posts / topics / engagement summary |

## Output

```
output/<PUBID>/
├── index.json      # every post (id, date, url, text, metrics, images)
├── images.json     # {url, file} manifest for download_images.py
├── posts/          # NNNN-YYYY-MM-DD-slug.md
├── images/         # downloaded JPEGs
└── REPORT.md       # analysis summary (optional)
```

## License

MIT
