---
name: linkedin-profile-archive
description: >-
  Archive every post of a LinkedIn profile (text + images + engagement metrics) into a
  local folder for offline analysis. Chronicles the hosted profile's full activity feed via
  LinkedIn's internal APIs, downloaded through a logged-in browser session (no paid API).
  Covers the full pipeline: launch a logged-in Chromium browser over CDP, capture the
  voyager/graphql feed request, paginate with the paginationToken until the last post, and
  download each post's images through the browser (Cloudflare blocks non-browser clients).
  Use when asked to "save all LinkedIn posts", "scrape a LinkedIn profile's posts", "archive
  LinkedIn activity/images", or analyze someone's LinkedIn output. Keywords: linkedin,
  profile, posts, voyage, scrap, archive, activity feed, images, engagement, CDP, Chromium.
license: MIT
compatibility: python 3.10+; websocket-client, requests (requests only for --curl mode);
  a Chrome/Chromium-family browser with a logged-in LinkedIn session
metadata:
  scripts: capture_feed.py, fetch_all_pages.py, linkedin_archive.py, download_images.py, linkedin_filter.py, linkedin_report.py
  output: index.json, posts/*.md, images/*.jpg, REPORT.md
---

# LinkedIn Profile Archiver

Archive all public posts of a LinkedIn profile (text + each post's image + like/comment/
share counts) into a structured local folder ready for analysis, fully offline, no API
subscription.

## When to Use

- "Guarda / archiva todos los posts de este perfil de LinkedIn" / "scrape a LinkedIn profile"
- You need someone's full posting history (text + images + metrics) for content analysis.
- The profile is reachable only through the user's logged-in `linkedin.com` session.

Do NOT use for: private data you have no right to access, bulk exports that violate
LinkedIn's ToS, or profiles the user is not authorized to read. Keep archives for analysis;
do not re-publish.

## How it works (technical design)

LinkedIn has **no public API** and blocks plain HTTP scraping (HTTP 999 + Cloudflare TLS
fingerprinting). The web app, however, loads the activity feed from internal endpoints:

```
GET /voyager/api/graphql?variables=(count:20,start:N,profileUrn:urn:li:fsd_profile:<PUBID>,paginationToken:<TOKEN>)&queryId=voyagerFeedDashProfileUpdates...
```

Each response is a RestLi JSON whose `*elements` hold update URNs resolved in `included[]`.
Pagination is driven by `data.data.<feed>.metadata.paginationToken`, **not** the `start`
offset. Image URLs are built from a truncated `rootUrl` + a signed `artifacts` segment
(`rootUrl + feedshare-shrink_800/<bucket>/<ts>?e=..&v=beta&t=..`). Those signed URLs only
serve through the browser session (Chrome/Cloudflare), not curl.

Cropping the profile's session cookies (Chromium v20 "app-bound" encryption) does not carry
across a copied profile, so the pipeline drives the user's **real, currently logged-in**
browser via CDP — launching it headful, navigating to the profile feed, and issuing the
feed/image requests from inside that page context.

## Procedure

### 0. Prereqs
```
pip install websocket-client requests
```
A Chromium-family browser (Chrome/Brave) running **with LinkedIn logged in**.

### 1. Launch the logged-in browser over CDP
Close any lingering instance of the same browser profile, then start it with the devtools
port and the user's real profile directory:
```
"<path>/brave.exe" --remote-debugging-port=9222 \
  "--user-data-dir=<path to User Data>" \
  --profile-directory=Default --window-size=1280,900 --restore-last-session
```
Wait until `http://127.0.0.1:9222/json/version` answers. Use `127.0.0.1`, not `localhost`
(Brave binds IPv4 and localhost may resolve to `::1`).

### 2. Capture the feed request
```
python capture_feed.py --url "https://www.linkedin.com/in/<PUBID>/recent-activity/all/" \
    --out session/capture --scrolls 8 --wait 2.5
```
Navigate + scrolls the activity page, captures every `voyager/api` JSON response, and writes
`session/capture/curl.txt` with the candidate feed request.

### 3. Identify & wire the feed endpoint
`capture_feed.py` may pick the wrong endpoint. `curl.txt` should point at the request whose
URL contains `count:20,start:0,profileUrn`. If not, fix `curl.txt` to that URL (plus the
`csrf-token` header). Then paginate everything:
```
python fetch_all_pages.py --endpoint session/capture/curl.txt --out session/pages --sleep 2
```
Stops when two consecutive pages return zero new updates. Result: `session/pages/page_NNN.json`.

### 4. Extract posts (text + metrics + image manifest)
```
python linkedin_archive.py --raw session/pages --out output/<PUBID>
```
Writes `index.json` (every post: id, date, url, text, metrics, image files), `posts/<num>-<date>-<slug>.md`,
and `images.json` (manifest of signed image URLs). Re-running resumes.

### 5. Download the images through the browser
```
python download_images.py --images output/<PUBID>/images.json --dir output/<PUBID>/images
```
Loads each image as an `<img>` inside the linkedin page and captures the binary body via CDP
(`Network.getResponseBody`). Resumes across runs and reconnects on WebSocket drops.

### 6. Analyze
```
python linkedin_report.py --index output/<PUBID>/index.json --md output/<PUBID>/REPORT.md
```

### 7. Filter to a date window (optional)
Keeps every field of the posts in range (full text, metrics, all images) into a new
folder — date-only filter, nothing is truncated:
```
python linkedin_filter.py --index output/<PUBID>/index.json --years 2 --out output/<PUBID>-2y
```

## Composition of output

```
output/<PUBID>/
├── index.json      # one object per post: id, date, url, author, text, metrics, images[]
├── images.json     # [{url, file}] manifest consumed by download_images.py
├── posts/          # NNNN-YYYY-MM-DD-slug.md per post (text + metric + image refs)
├── images/         # downloaded image files (NNNN-NN.jpg)
└── REPORT.md       # optional: cadence, top posts, topics, engagement summary
```

## Pitfalls

- **paginationToken is mandatory.** Using only `start:N` returns the same first page every
  time. Always propagate `data...metadata.paginationToken`.
- **RestLi keys.** Update lists live under `*elements` (leading star), not `elements`.
- **Truncated image URLs.** The feed JSON's `rootUrl` ends in `feedshare-` with no signature;
  the signed part is in the sibling `artifacts[].fileIdentifyingUrlPathSegment`. Build
  `rootUrl + segment` to get a downloadable URL. Exclude avatar `rootUrl`s
  (`profile-displayphoto`).
- **Cookies can't be copied.** Chromium v20 app-bound encryption keeps `li_at` from
  transferring to a copied profile. Drive the user's real logged-in browser; do not strip
  session cookies.
- **media.licdn.com 403s curl/requests** (Cloudflare fingerprinting) even with cookies.
  Download images **through the browser** (CDP), not with an HTTP client.
- **Use 127.0.0.1** for the CDP endpoint, not localhost (IPv6 resolution).
- **Detached background runs** over SSH/terminal that get killed when the parent exits:
  launch with `subprocess.DETACHED_PROCESS` or a proper `cmd start` title.
- **Feed endpoint selection.** Don't trust the first voyager hit; match the `profileUrn` +
  `count:20,start:0` feed shape. Check each page has non-empty `*elements`.
- **Resume safety.** `linkedin_archive.py` skips posts already in `index.json`; reruns are idempotent.

## Verification

- `session/pages` contains multiple `page_NNN.json`; the last two have zero new updates.
- `index.json` has as many posts as the max count indicated by pagination (e.g. 2,000+).
- Each post `.md` exists, contains the text, has the correct number of image refs.
- `images/` files are valid JPEG (non-zero, openable), count matches `images.json`.
- `REPORT.md` lists the date range, cadence, top posts and topics.
