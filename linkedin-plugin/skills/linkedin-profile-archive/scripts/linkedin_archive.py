#!/usr/bin/env python3
"""
linkedin_archive.py — Archive all posts of a LinkedIn profile (text + images + metrics)
from raw JSON pages of LinkedIn's internal voyager/graphql API.

Two modes
---------
--raw DIR   Process already-saved raw JSON pages (produced by capture_feed.py +
            fetch_all_pages.py). This is the primary path: pages carry the
            session-bound data, extraction is local.

--curl FILE Replay a DevTools 'Copy as cURL' request with pagination. Only works
            when session cookies are replayable from Python (e.g. older cookie
            encryption); with Chromium v20 app-bound cookies this fails — use
            the browser-based path instead.

Pipeline
--------
    python capture_feed.py --url "https://www.linkedin.com/in/<slug>/recent-activity/all/" --out session/capture
    python fetch_all_pages.py --endpoint session/capture/curl.txt --out session/pages
    python linkedin_archive.py --raw session/pages --out output/<slug>
    python download_images.py --images output/<slug>/images.json --dir output/<slug>/images

Output
------
    out/
    ├── index.json          # every post: id, date, url, text, metrics, image files
    ├── images.json         # manifest for download_images.py
    └── posts/
        └── NNNN-YYYY-MM-DD-slug.md

Resume: re-running with the same --out skips posts already in index.json.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import time
from pathlib import Path

try:
    import requests  # only needed for --curl mode
except ImportError:
    requests = None

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

# --------------------------------------------------------------------------
# Post extraction (generic, resilient to shape changes)
# --------------------------------------------------------------------------

AVATAR_RE = re.compile(
    r"profile-displayphoto|ghost|shields|safe-image|backgroundimage", re.I
)


def walk(obj, prefix=""):
    """Yield (path, value) pairs for every node in a JSON tree."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def _leaf(path: str, key: str) -> bool:
    return path == key or path.endswith("." + key)


def find_text(update: dict) -> str:
    """Post commentary text: commentary → text → text, with fallbacks."""
    commentary = None
    if isinstance(update.get("commentary"), dict):
        commentary = update["commentary"]
    else:
        for path, val in walk(update):
            if path.endswith(".commentary") and isinstance(val, dict):
                commentary = val
                break
    if commentary is not None:
        t = commentary.get("text")
        if isinstance(t, dict) and isinstance(t.get("text"), str):
            return t["text"]
        if isinstance(t, str):
            return t
        tv = commentary.get("textValue")
        if isinstance(tv, str):
            return tv
    # fallback: longest 'text'-keyed string under the update
    best = ""
    for path, val in walk(update):
        if _leaf(path, "text") and isinstance(val, str) and len(val) > len(best):
            best = val
    return best


def activity_id(update: dict) -> str:
    """Numeric activity ID from backendUrn / entityUrn / updateId."""
    meta = update.get("metadata")
    if isinstance(meta, dict) and isinstance(meta.get("backendUrn"), str):
        m = re.search(r"urn:li:activity:(\d+)", meta["backendUrn"])
        if m:
            return m.group(1)
    for path, val in walk(update):
        if _leaf(path, "updateId") and isinstance(val, str):
            m = re.search(r"urn:li:activity:(\d+)", val)
            if m:
                return m.group(1)
            return val
    for path, val in walk(update):
        if _leaf(path, "entityUrn") and isinstance(val, str):
            m = re.search(r"urn:li:activity:(\d+)", val)
            if m:
                return m.group(1)
    return ""


def find_date(update: dict, aid: str) -> str | None:
    """Explicit postedAt if present; else decode the snowflake activity ID:
    LinkedIn activity IDs encode the creation time in their top bits (id >> 22 ms)."""
    for path, val in walk(update):
        if _leaf(path, "postedAt") and isinstance(val, (int, float)):
            return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(val / 1000))
        if _leaf(path, "firstPostedAt") and isinstance(val, (int, float)):
            return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(val / 1000))
        if _leaf(path, "time") and isinstance(val, (int, float)) and val > 1e11:
            return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(val / 1000))
    if aid.isdigit():
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime((int(aid) >> 22) / 1000))
    return None


def find_author(update: dict) -> str | None:
    actor = update.get("actor")
    if isinstance(actor, dict):
        name = actor.get("name")
        if isinstance(name, dict) and isinstance(name.get("text"), str):
            return name["text"]
    for path, val in walk(update):
        if _leaf(path, "miniProfile") and isinstance(val, dict):
            parts = [val.get("firstName", ""), val.get("lastName", "")]
            name = " ".join(p for p in parts if p).strip()
            if name:
                return name
    return None


def find_share_url(update: dict, aid: str) -> str:
    sc = update.get("socialContent")
    if isinstance(sc, dict) and isinstance(sc.get("shareUrl"), str):
        url = re.sub(r"[?&]utm_[^&]+", "", sc["shareUrl"])
        return url
    return f"https://www.linkedin.com/feed/update/urn:li:activity:{aid}/"


def find_images(update: dict) -> list[str]:
    """Post images = full signed media.licdn.com URLs built from rootUrl + artifacts.
    The feed JSON gives truncated rootUrl (''…feedshare-) with no signature, but each
    post's VectorImage carries signed artifacts (fileIdentifyingUrlPathSegment) that
    complete the URL: full = rootUrl + segment (e.g. feedshare-shrink_800/<bucket>/…
    ?e=…&t=…). Returns full descending-path URLs, best resolution first."""
    urls: list[tuple[int, str]] = []
    for path, val in walk(update):
        if _leaf(path, "rootUrl") and isinstance(val, str) and "media.licdn.com" in val:
            urls.append((0, val))
    if urls:
        # each rootUrl + its artifacts already implies a full URL; build them
        full = []
        seen = set()
        # find the VectorImage dict(s): has rootUrl + artifacts
        def walk_dicts(node):
            if isinstance(node, dict):
                yield node
                for v in node.values():
                    yield from walk_dicts(v)
            elif isinstance(node, list):
                for v in node:
                    yield from walk_dicts(v)

        for d in walk_dicts(update):
            root = d.get("rootUrl")
            if not isinstance(root, str) or "media.licdn.com" not in root or root in seen:
                continue
            # skip avatars / profile images; keep only post feed images
            if AVATAR_RE.search(root) or "displayphoto" in root.lower():
                continue
            seen.add(root)
            arts = d.get("artifacts")
            if not isinstance(arts, list):
                continue
            # best resolutions first
            ranked = sorted(
                arts,
                key=lambda a: {"image-high-res": 5, "shrink_1280": 4, "shrink_800": 3, "shrink_480": 2, "shrink_160": 1}.get(
                    (a.get("fileIdentifyingUrlPathSegment") or "").split("/")[0], 0
                ),
                reverse=True,
            )
            best = ranked[0] if ranked else None
            if best and best.get("fileIdentifyingUrlPathSegment"):
                # ensure the segment part after root's trailing token: root ends in
                # 'feedshare-' or 'profile-displayphoto-'; the artifact starts with the
                # resolution token (shrink_*/image-high-res)
                root_clean = root if root.endswith("/") else root + ""
                # if root already ends with 'feedshare-shrink_800/' style, keep as-is
                seg = best["fileIdentifyingUrlPathSegment"]
                # strip any resolution part already present in root
                full_url = None
                if re.search(r"(feedshare|displayphoto)-(shrink_|image-)", root):
                    full_url = root + seg.split("/", 1)[-1] if seg.split("/")[0] == "" else root + seg
                else:
                    full_url = root + seg
                full.append(full_url)
        return full
    # fallback: any raw media.licdn.com URL not avatar-like
    out = []
    seen = set()
    for path, val in walk(update):
        if isinstance(val, str) and "media.licdn.com" in val and val not in seen and not AVATAR_RE.search(val):
            seen.add(val)
            out.append(val)
    return out


def find_metrics(update: dict, sac_by_activity: dict | None = None) -> dict:
    out = {}
    aid = activity_id(update)
    if sac_by_activity and aid in sac_by_activity:
        sac = sac_by_activity[aid]
        for key in ("numLikes", "numComments", "numShares", "numReposts", "numReactions"):
            if key in sac and isinstance(sac[key], (int, float)):
                out[key[3:].lower()] = int(sac[key])
        return out
    for key in ("numLikes", "numComments", "numShares", "numReposts", "numReactions"):
        for path, val in walk(update):
            if _leaf(path, key) and isinstance(val, (int, float)):
                out[key[3:].lower()] = int(val)
                break
    return out


def slugify(text: str, max_len: int = 60) -> str:
    words = re.findall(r"[a-z0-9áéíóúñü]+", text.lower())
    slug = "-".join(words[:8])[:max_len].strip("-")
    return slug or "post"


# --------------------------------------------------------------------------
# Raw-page processing (primary path)
# --------------------------------------------------------------------------

def load_pages(pages_dir: Path) -> list[dict]:
    out = []
    for f in sorted(pages_dir.glob("page_*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"  ⚠ skipping {f.name}: {e}")
    return out


def process_pages(pages_dir: Path, out: Path, max_posts: int = 0) -> tuple[list[dict], list[dict]]:
    pages = load_pages(pages_dir)
    if not pages:
        raise SystemExit("✗ no page_*.json files found")
    print(f"→ processing {len(pages)} raw pages")

    posts_dir = out / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    index_path = out / "index.json"
    known: dict[str, dict] = {}
    if index_path.exists():
        known = {p["id"]: p for p in json.loads(index_path.read_text(encoding="utf-8"))}
        print(f"ℹ resuming: {len(known)} posts already archived")

    order = len(known)
    images_manifest: list[dict] = []
    image_num = 1

    for pi, page in enumerate(pages):
        by_urn = {}
        sac_by_activity = {}
        for ent in page.get("included", []) or []:
            if not isinstance(ent, dict):
                continue
            u = ent.get("entityUrn") or ent.get("urn") or ent.get("$urn")
            if u:
                by_urn[u] = ent
            if (ent.get("$type") or "").endswith("SocialActivityCounts"):
                m = re.search(r"urn:li:activity:(\d+)", str(u))
                if m:
                    sac_by_activity[m.group(1)] = ent

        feed = None
        data = page.get("data", page)
        if isinstance(data, dict):
            def find_feed(node: dict, depth: int):
                if depth > 6:
                    return None
                if isinstance(node.get("*elements"), list) and node.get("*elements"):
                    return node
                for v in node.values():
                    if isinstance(v, dict):
                        r = find_feed(v, depth + 1)
                        if r:
                            return r
                return None
            feed = find_feed(data, 0)
        if not feed:
            continue
        elements = feed["*elements"]

        for el in elements:
            update = by_urn.get(el, el) if isinstance(el, str) else el
            if not isinstance(update, dict):
                continue
            aid = activity_id(update)
            if not aid or aid in known:
                continue
            text = find_text(update)
            date = find_date(update, aid) or "unknown"
            metrics = find_metrics(update, sac_by_activity)
            author = find_author(update)
            images = find_images(update)

            order += 1
            num = f"{order:04d}"
            date_part = (date or "unknown")[:10]
            fname = f"{num}-{date_part}-{slugify(text)}.md"
            post = {
                "id": aid,
                "num": num,
                "date": date,
                "url": find_share_url(update, aid),
                "author": author,
                "text": text,
                "metrics": metrics,
                "images": [],
            }
            img_files = []
            for img_url in images:
                f = f"{num}-{image_num:02d}.jpg"
                image_num += 1
                img_files.append(f)
                images_manifest.append({"url": img_url, "file": f})
            post["images"] = img_files
            known[aid] = post

            md = [f"# {date_part} · {author or 'LinkedIn'}", ""]
            md.append(f"**URL:** {post['url']}")
            md.append(f"**Fecha:** {date}")
            if metrics:
                md.append("**Métricas:** " + " · ".join(f"{k}: {v}" for k, v in metrics.items()))
            md.append("")
            md.append(text if text else "*[sin texto]*")
            md.append("")
            for f in img_files:
                md.append(f"![imagen](images/{f})")
                md.append("")
            (posts_dir / fname).write_text("\n".join(md), encoding="utf-8")

        if pi % 10 == 0 or pi == len(pages) - 1:
            index_path.write_text(json.dumps(list(known.values()), ensure_ascii=False, indent=2), encoding="utf-8")
        if max_posts and order >= max_posts:
            print(f"✓ reached --max-posts {max_posts}")
            break
        print(f"  … page {pi + 1}/{len(pages)} ({order} posts so far)")

    index_path.write_text(json.dumps(list(known.values()), ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "images.json").write_text(json.dumps(images_manifest, indent=2), encoding="utf-8")
    return list(known.values()), images_manifest


# --------------------------------------------------------------------------
# cURL replay mode (secondary; only when cookies are replayable)
# --------------------------------------------------------------------------

def parse_curl(text: str) -> dict:
    import shlex
    tokens = shlex.split(text)
    if tokens and tokens[0] == "curl":
        tokens = tokens[1:]
    url = None
    method = None
    headers: dict[str, str] = {}
    body = None
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "--url" and i + 1 < len(tokens):
            url = tokens[i + 1]
            i += 2
            continue
        if tok.startswith("--url="):
            url = tok.split("=", 1)[1]
        elif tok == "-H" and i + 1 < len(tokens):
            k, _, v = tokens[i + 1].partition(":")
            headers[k.strip().lower()] = v.strip()
            i += 2
            continue
        elif tok == "-X" and i + 1 < len(tokens):
            method = tokens[i + 1].upper()
            i += 2
            continue
        elif tok in ("--data-raw", "--data", "--data-binary") and i + 1 < len(tokens):
            body = tokens[i + 1]
            i += 2
            continue
        elif tok.startswith("--data-raw=") or tok.startswith("--data="):
            body = tok.split("=", 1)[1]
        elif not tok.startswith("-") and url is None:
            url = tok
        i += 1
    if not url:
        raise SystemExit("✗ No URL found in the cURL command")
    return {"method": method or ("POST" if body else "GET"), "url": url, "headers": headers, "body": body}


def bump_start(url: str, new_start: int) -> str:
    if re.search(r"start:\d+", url):
        return re.sub(r"start:\d+", f"start:{new_start}", url)
    return re.sub(r"[?&]start=\d+", f"?start={new_start}", url)


def set_pagination_token(url: str, token: str) -> str:
    import urllib.parse
    url = re.sub(r",?paginationToken:[^,()]*(?=\)|,)", "", url)
    m = re.search(r"variables=\(", url)
    if not m:
        return url
    depth = 0
    end = None
    for i in range(m.end() - 1, len(url)):
        if url[i] == "(":
            depth += 1
        elif url[i] == ")":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        return url
    tok = urllib.parse.quote(token, safe="")
    return url[:end] + f",paginationToken:{tok}" + url[end:]


def page_token(payload: dict) -> str:
    data = payload.get("data", payload) if isinstance(payload, dict) else {}

    def find(node, depth):
        if depth > 6 or not isinstance(node, dict):
            return ""
        meta = node.get("metadata")
        if isinstance(meta, dict) and meta.get("paginationToken"):
            return meta["paginationToken"]
        for v in node.values():
            t = find(v, depth + 1)
            if t:
                return t
        return ""

    return find(data, 0) if isinstance(data, dict) else ""


def find_feed_node(payload: dict):
    data = payload.get("data", payload) if isinstance(payload, dict) else {}
    if not isinstance(data, dict):
        return None

    def find(node: dict, depth: int):
        if depth > 6 or not isinstance(node, dict):
            return None
        elements = node.get("*elements") or node.get("elements")
        if isinstance(elements, list) and elements and isinstance(node.get("paging"), dict):
            return node
        for v in node.values():
            if isinstance(v, dict):
                r = find(v, depth + 1)
                if r:
                    return r
        return None

    return find(data, 0)


def replay_curl(curl_file: Path, out: Path, max_posts: int, sleep_s: float) -> None:
    if requests is None:
        raise SystemExit("✗ --curl mode needs the 'requests' package")
    curl = parse_curl(curl_file.read_text(encoding="utf-8"))
    headers = dict(curl["headers"])
    headers.setdefault("user-agent", UA)
    url = curl["url"]
    start = 0
    m = re.search(r"start:(\d+)", url) or re.search(r"[?&]start=(\d+)", url)
    if m:
        start = int(m.group(1))
    token = ""
    page = 0
    seen: set[str] = set()

    session = requests.Session()
    while True:
        page_url = bump_start(url, start)
        if token:
            page_url = set_pagination_token(page_url, token)
        if curl["method"] == "GET":
            r = session.get(page_url, headers=headers, timeout=60)
        else:
            r = session.request(curl["method"], page_url, data=curl["body"], headers=headers, timeout=60)
        if r.status_code == 429:
            print("⏳ 429, waiting 30s")
            time.sleep(30)
            continue
        if r.status_code in (401, 403):
            raise SystemExit("✗ session expired (401/403). Use the browser path (capture_feed + fetch_all_pages).")
        if r.status_code >= 400:
            print(f"⚠ HTTP {r.status_code}: {r.text[:200]}")
            break
        try:
            payload = r.json()
        except Exception:
            print(f"⚠ non-JSON page: {r.text[:200]}")
            break

        pages_dir = out / "raw"
        pages_dir.mkdir(parents=True, exist_ok=True)
        (pages_dir / f"page_{page:03d}.json").write_text(json.dumps(payload, indent=2)[: 3_000_000], encoding="utf-8")

        feed = find_feed_node(payload)
        if not feed:
            print("✓ no feed in response — done")
            break
        elements = feed.get("*elements") or feed.get("elements") or []
        by_urn = {}
        for ent in payload.get("included", []) or []:
            if isinstance(ent, dict):
                u = ent.get("entityUrn") or ent.get("urn")
                if u:
                    by_urn[u] = ent
        updates = [by_urn.get(el, el) if isinstance(el, str) else el for el in elements]
        new_ids = 0
        for u in updates:
            aid = activity_id(u) if isinstance(u, dict) else ""
            if aid and aid not in seen:
                seen.add(aid)
                new_ids += 1
        print(f"✔ page {page} start={start} updates={len(updates)} new={new_ids}")
        if new_ids == 0:
            break

        nxt_token = page_token(payload)
        if nxt_token:
            token = nxt_token
        start += 20
        page += 1
        if max_posts and len(seen) >= max_posts:
            break
        time.sleep(sleep_s)

    print(f"=== captured {len(seen)} updates into {out / 'raw'} — now run: linkedin_archive.py --raw {out / 'raw'} --out {out}")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="directory with raw page_*.json files (primary path)")
    ap.add_argument("--curl", help="cURL file to replay (secondary path)")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--max-posts", type=int, default=0, help="stop after N posts")
    ap.add_argument("--sleep", type=float, default=1.5, help="seconds between pages (--curl mode)")
    args = ap.parse_args()

    if args.raw:
        posts, manifest = process_pages(Path(args.raw), Path(args.out), args.max_posts)
        total = len(posts)
        with_imgs = sum(1 for p in posts if p["images"])
        print(f"\n=== done: {total} posts → {args.out}")
        print(f"    {with_imgs} with images; {len(manifest)} image URLs in {args.out}/images.json")
        if manifest:
            print(f"    next: download_images.py --images {args.out}/images.json --dir {args.out}/images")
    elif args.curl:
        replay_curl(Path(args.curl), Path(args.out), args.max_posts, args.sleep)
    else:
        ap.error("pass --raw DIR or --curl FILE")


if __name__ == "__main__":
    main()
