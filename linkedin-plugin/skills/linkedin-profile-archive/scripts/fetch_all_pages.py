#!/usr/bin/env python3
"""
fetch_all_pages.py — Paginate a captured LinkedIn voyager feed request from INSIDE
the logged-in browser page (CDP), saving every raw JSON response to disk.

Why in-page?
------------
LinkedIn encrypts session cookies (Chromium v20 app-bound) so they cannot be
copied to another browser profile or replayed from a plain HTTP client. But the
browser's own page context can fetch the voyager API transparently (it decrypts
the cookies itself). This script drives that pagination loop over CDP and dumps
the JSON pages for later extraction with linkedin_archive.py --raw.

Usage
-----
    python fetch_all_pages.py --endpoint session/capture/curl.txt \
        --out session/pages --port 9222 [--max-pages 200] [--sleep 2]

The --endpoint file is the curl.txt emitted by capture_feed.py.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import websocket
import urllib.request


def parse_curl_file(path: Path) -> dict:
    """Reuse the cURL format: extract url + the csrf-token header (enough)."""
    text = path.read_text(encoding="utf-8")
    url = re.search(r"'(https?://[^']+)'", text)
    if not url:
        raise SystemExit(f"✗ no URL in {path}")
    csrf = re.search(r"-H 'csrf-token: ([^']+)'", text)
    return {
        "url": url.group(1),
        "csrf": csrf.group(1) if csrf else "",
    }


def bump_start(url: str, new_start: int) -> str:
    if re.search(r"start:\d+", url):
        return re.sub(r"start:\d+", f"start:{new_start}", url)
    return re.sub(r"[?&]start=\d+", f"?start={new_start}", url)


def set_pagination_token(url: str, token: str) -> str:
    """Insert/replace paginationToken inside variables=(...), keeping paren balance."""
    import urllib.parse

    # drop any existing token variable
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
    """paginationToken from the response metadata, if present (recursive)."""
    data = payload.get("data", payload) if isinstance(payload, dict) else {}
    if not isinstance(data, dict):
        return ""

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

    return find(data, 0)


def page_updates(payload: dict) -> tuple[list, dict | None]:
    """Generic: find the first subtree under data with a non-empty elements list
    and a paging object (feed shape: data.data.feedDashProfileUpdatesByMemberShareFeed)."""
    data = payload.get("data", payload) if isinstance(payload, dict) else {}
    if not isinstance(data, dict):
        return [], None

    def find(node: dict, depth: int):
        if depth > 6 or not isinstance(node, dict):
            return None
        elements = node.get("elements") or node.get("*elements")  # RestLi lists use *elements
        if isinstance(elements, list) and elements and isinstance(node.get("paging"), dict):
            return elements, node["paging"]
        for v in node.values():
            found = find(v, depth + 1) if isinstance(v, dict) else None
            if found:
                return found
        return None

    found = find(data, 0)
    if found:
        return found
    # last resort: any list named elements/*elements
    for v in data.values():
        if isinstance(v, dict):
            el = v.get("elements") or v.get("*elements")
            if isinstance(el, list) and el:
                return el, v.get("paging")
    return [], None


def connect_page(port: int) -> websocket.WebSocket:
    tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5))
    pages = [t for t in tabs if t["type"] == "page"]
    if not pages:
        raise SystemExit("✗ no page tabs open in the browser")
    print("  page tabs:")
    for t in pages[:6]:
        print(f"    - {t.get('url','')[:90]}")
    return websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)


def cdp_call(ws: websocket.WebSocket, method: str, params: dict, mid: int) -> dict:
    ws.send(json.dumps({"id": mid, "method": method, "params": params}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == mid:
            if "error" in msg:
                raise RuntimeError(f"CDP {method}: {msg['error']}")
            return msg.get("result", {})


def in_page_fetch(ws: websocket.WebSocket, url: str, csrf: str, mid: int) -> dict:
    """Run fetch() in the page context; returns parsed JSON (or error info)."""
    expr = f"""
    fetch('{url}', {{
        method: 'GET',
        credentials: 'include',
        headers: {{'csrf-token': '{csrf}', 'accept': 'application/vnd.linkedin.normalized+json+2.1', 'x-restli-protocol-version': '2.0.0'}}
    }}).then(async r => {{
        const t = await r.text();
        return JSON.stringify({{status: r.status, body: t}});
    }}).catch(e => JSON.stringify({{status: 0, body: String(e)}}))
    """
    res = cdp_call(ws, "Runtime.evaluate", {"expression": expr, "awaitPromise": True, "returnByValue": True}, mid)
    raw = res.get("result", {}).get("value", "{}")
    try:
        out = json.loads(raw)
    except Exception:
        return {"status": -1, "body": raw[:500]}
    if out.get("body", "").startswith(")]}'"):
        out["body"] = out["body"][4:]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--endpoint", required=True, help="curl.txt from capture_feed.py (feed request)")
    ap.add_argument("--out", default="session/pages", help="output dir for raw JSON pages")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--max-pages", type=int, default=300)
    ap.add_argument("--sleep", type=float, default=2.0)
    args = ap.parse_args()

    ep = parse_curl_file(Path(args.endpoint))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    ws = connect_page(args.port)
    print(f"✔ connected; endpoint: {ep['url'][:90]}…")

    start = 0
    token = ""
    mid = 100
    page_no = 0
    seen_ids: set[str] = set()
    empty_pages = 0

    while page_no < args.max_pages:
        mid += 1
        url = bump_start(ep["url"], start)
        if token:
            url = set_pagination_token(url, token)
        res = in_page_fetch(ws, url, ep["csrf"], mid)
        if res.get("status") == 429:
            print(f"⏳ 429 — waiting 30s…")
            time.sleep(30)
            continue
        if res.get("status") == 401 or res.get("status") == 403:
            print("✗ session expired (401/403) — reopen the profile's LinkedIn tab and retry")
            break
        if res.get("status") != 200:
            print(f"⚠ HTTP {res.get('status')}: {str(res.get('body'))[:200]}")
            break

        try:
            payload = json.loads(res["body"])
        except Exception:
            print(f"⚠ page {page_no} is not JSON: {res['body'][:200]}")
            break
        if page_no == 0:
            print(f"  body sample: {res['body'][:160]}")

        updates, paging = page_updates(payload)
        # RestLi: *elements may hold URN strings resolved in payload['included']
        by_urn = {}
        for ent in payload.get("included", []) or []:
            if isinstance(ent, dict):
                u = ent.get("entityUrn") or ent.get("urn") or ent.get("$urn")
                if u:
                    by_urn[u] = ent
        resolved = []
        for u in updates:
            if isinstance(u, str):
                ent = by_urn.get(u)
                if ent is not None:
                    resolved.append(ent)
            elif isinstance(u, dict):
                resolved.append(u)
        updates = resolved
        new_count = 0
        for u in updates:
            uid = u.get("updateId") or u.get("entityUrn") or u.get("urn") or ""
            if uid and uid not in seen_ids:
                seen_ids.add(uid)
                new_count += 1

        fname = out / f"page_{page_no:03d}.json"
        fname.write_text(json.dumps(payload, indent=2)[: 3_000_000], encoding="utf-8")
        print(f"✔ page {page_no:03d} start={start} updates={len(updates)} new={new_count} → {fname.name}")

        if new_count == 0:
            empty_pages += 1
            if empty_pages >= 2:
                print("✓ two consecutive empty pages — done")
                break
        else:
            empty_pages = 0

        # next offset: paginationToken from metadata (authoritative), else paging.nextStart
        nxt_token = page_token(payload)
        if nxt_token:
            token = nxt_token
        nxt = None
        if isinstance(paging, dict) and paging.get("nextStart") is not None:
            nxt = int(paging["nextStart"])
        start = nxt if nxt is not None else start + 20
        page_no += 1
        time.sleep(args.sleep)

    print(f"\n=== done: {page_no} pages, {len(seen_ids)} unique updates → {out}")
    ws.close()


if __name__ == "__main__":
    main()
