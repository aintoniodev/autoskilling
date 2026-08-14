#!/usr/bin/env python3
"""
capture_feed.py — Capture LinkedIn's internal voyager API requests from a live
browser (CDP), so the feed can be replayed and archived without manual cURL copying.

Why this exists
---------------
LinkedIn blocks bots and has no public API for profile posts. The web app, however,
loads every post through internal endpoints (voyager/api/...). This script drives a
browser that has a logged-in LinkedIn session (e.g. an isolated copy of the user's
profile), intercepts those internal requests via CDP, saves the raw JSON responses
AND emits a DevTools-style cURL file that linkedin_archive.py can replay with
pagination to get every post.

Usage
-----
    python capture_feed.py --url "https://www.linkedin.com/in/<slug>/recent-activity/all/" \
        --out session/capture --scrolls 5

Output
------
    session/capture/
    ├── requests.json      # every intercepted voyager request (url/method/headers/body/status)
    ├── pages/*.json       # raw JSON response bodies
    ├── curl.txt           # the chosen feed request, ready for linkedin_archive.py --curl
    └── screenshot.png     # last viewport, for sanity checks
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import websocket

try:
    import requests as http
except ImportError:
    http = None


class CDP:
    def __init__(self, ws_url: str):
        # suppress_origin: Chrome >=111 rejects WS handshakes carrying an Origin
        # header unless launched with --remote-allow-origins=*
        self.ws = websocket.create_connection(ws_url, timeout=30, suppress_origin=True)
        self._id = 0
        self._pending: dict[int, dict] = {}
        self._events: list[dict] = []

    def send(self, method: str, params: dict | None = None, timeout: float = 30) -> dict:
        self._id += 1
        mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            raw = self.ws.recv()
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", "replace")
            msg = json.loads(raw)
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"CDP {method}: {msg['error']}")
                return msg.get("result", {})
            if "method" in msg:
                self._events.append(msg)

    def drain(self, method: str, max_wait: float = 0.05) -> list[dict]:
        """Collect events of a given method that arrived since last drain."""
        out = []
        for ev in self._events:
            if ev.get("method") == method:
                out.append(ev)
        self._events = [ev for ev in self._events if ev.get("method") != method]
        return out

    def wait_event(self, method: str, timeout: float = 20) -> dict:
        deadline = time.time() + timeout
        while time.time() < deadline:
            for ev in self._events:
                if ev.get("method") == method:
                    self._events.remove(ev)
                    return ev
            self.ws.settimeout(min(1.0, deadline - time.time()))
            try:
                raw = self.ws.recv()
            except websocket.WebSocketTimeoutException:
                continue
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", "replace")
            msg = json.loads(raw)
            if "method" in msg:
                if msg["method"] == method:
                    return msg
                self._events.append(msg)
        raise TimeoutError(f"no {method} event")

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


def new_tab(port: int) -> str:
    """Create a tab and return its page-level WS URL."""
    base = f"http://127.0.0.1:{port}"  # localhost may resolve to ::1; Brave binds IPv4
    if http:
        r = http.put(f"{base}/json/new?url=about:blank", timeout=10)
        return r.json()["webSocketDebuggerUrl"]
    import urllib.request

    req = urllib.request.Request(
        f"{base}/json/new?url=about:blank", method="PUT"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)["webSocketDebuggerUrl"]


AUTHWALL_MARKERS = ("authwall", "join now", "regístrate", "crea una cuenta")
LOGIN_MARKERS = ("iniciar sesión", "sign in", "verify to continue", "verificación")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", required=True, help="activity feed URL to capture")
    ap.add_argument("--out", default="session/capture", help="output dir")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--scrolls", type=int, default=6, help="scroll passes to trigger more pages")
    ap.add_argument("--wait", type=float, default=2.5, help="seconds between scrolls")
    args = ap.parse_args()

    out = Path(args.out)
    pages_dir = out / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    ws_url = new_tab(args.port)
    cdp = CDP(ws_url)
    print("✔ tab created")

    cdp.send("Network.enable")
    cdp.send("Page.enable")
    cdp.send("Runtime.enable")

    requests_meta: dict[str, dict] = {}
    responses: list[dict] = []
    saved_pages: list[str] = []

    cdp.send("Page.navigate", {"url": args.url})
    print(f"→ navigating {args.url[:90]}…")
    try:
        cdp.wait_event("Page.loadEventFired", timeout=30)
    except TimeoutError:
        print("⚠ no load event (page may be blocked)")

    time.sleep(3)

    def drain_network():
        for ev in cdp.drain("Network.requestWillBeSent"):
            p = ev["params"]
            req = p["request"]
            requests_meta[p["requestId"]] = {
                "url": req.get("url"),
                "method": req.get("method"),
                "headers": req.get("headers", {}),
                "postData": req.get("postData", ""),
                "frame": p.get("frameId", "")[:8],
            }
        for ev in cdp.drain("Network.responseReceived"):
            p = ev["params"]
            rid = p["requestId"]
            if rid in requests_meta:
                requests_meta[rid]["status"] = p["response"].get("status")
                requests_meta[rid]["mimeType"] = p["response"].get("mimeType", "")

    # check auth state before scrolling
    state = cdp.send(
        "Runtime.evaluate",
        {
            "expression": "JSON.stringify({url: location.href, title: document.title, text: document.body ? document.body.innerText.slice(0,400) : ''})",
            "returnByValue": True,
        },
    )
    page_snapshot = json.loads(state.get("result", {}).get("value", "{}"))
    body_text = (page_snapshot.get("text") or "").lower()
    cdp.send(
        "Page.captureScreenshot",
        {"format": "png", "captureBeyondViewport": False},
        timeout=15,
    )
    # screenshot result is base64; save
    shot = cdp.send("Page.captureScreenshot", {"format": "png"}, timeout=15)
    import base64

    (out / "screenshot.png").write_bytes(base64.b64decode(shot.get("data", "")))
    print(f"✔ page: {page_snapshot.get('title','')[:60]} | {page_snapshot.get('url','')[:80]}")

    if any(m in body_text for m in AUTHWALL_MARKERS) or "linkedin.com/authwall" in page_snapshot.get("url", ""):
        print("✗ AUTHWALL — the copied session is not logged in.")
        print("  Re-copy the Brave/Chrome profile while logged in, then retry.")
        cdp.close()
        return
    print("✔ session looks logged-in (no authwall)")

    # scroll to trigger feed pagination, capturing voyager traffic
    scroll_expr = """
    (() => {
      const before = document.body.scrollHeight;
      window.scrollTo(0, document.body.scrollHeight);
      return before;
    })()
    """
    for i in range(args.scrolls):
        cdp.send("Runtime.evaluate", {"expression": scroll_expr})
        time.sleep(args.wait)
        drain_network()
        # save any voyager JSON response bodies we have so far
        for rid, meta in requests_meta.items():
            if rid in [r["requestId"] for r in responses]:
                continue
            if "voyager/api" not in (meta.get("url") or ""):
                continue
            if meta.get("method") == "OPTIONS":
                continue
            if not (meta.get("mimeType", "").startswith("application/json") or meta.get("status") == 200):
                continue
            try:
                body = cdp.send("Network.getResponseBody", {"requestId": rid}, timeout=15)
                content = body.get("body", "")
                if content.startswith(")]}'"):
                    content = content[4:]
                try:
                    parsed = json.loads(content)
                except Exception:
                    continue
                responses.append({"requestId": rid, "request": meta, "json": parsed})
                (pages_dir / f"page_{len(saved_pages):03d}.json").write_text(
                    json.dumps(parsed, indent=2)[: 3_000_000], encoding="utf-8"
                )
                saved_pages.append(rid)
                n_updates = 0
                s = json.dumps(parsed)[:500]
                m = re.search(r'"updates"\s*:\s*\[', s)
                print(f"  📦 voyager {meta['method']} {meta['url'][:80]}… status={meta.get('status')} saved={len(saved_pages)}")
            except Exception as e:
                print(f"  ⚠ body fetch failed for {rid[:12]}: {e}")
        cdp.drain("Network.loadingFinished")

    # final pass for any remaining responses
    for rid, meta in requests_meta.items():
        if rid in [r["requestId"] for r in responses]:
            continue
        if "voyager/api" not in (meta.get("url") or ""):
            continue
        try:
            body = cdp.send("Network.getResponseBody", {"requestId": rid}, timeout=15)
            content = body.get("body", "")
            if content.startswith(")]}'"):
                content = content[4:]
            parsed = json.loads(content)
            responses.append({"requestId": rid, "request": meta, "json": parsed})
            (pages_dir / f"page_{len(saved_pages):03d}.json").write_text(
                json.dumps(parsed, indent=2)[: 3_000_000], encoding="utf-8"
            )
            saved_pages.append(rid)
        except Exception:
            pass

    # ---- pick the feed request ----
    def score(r: dict) -> int:
        s = json.dumps(r["json"])
        hits = sum(1 for k in ("dashUpdates", "feedUpdates", '"updates"', "updateMetadata", "commentary") if k in s)
        return hits + len(s) // 1_000_000

    if not responses:
        print("✗ no voyager JSON captured — did the feed load? See screenshot.png")
        cdp.close()
        return

    feed = max(responses, key=score)
    req = feed["request"]

    # write cURL file for linkedin_archive.py
    lines = ["curl"]
    lines.append(f"-X {req['method']}")
    lines.append(f"'{req['url']}'")
    for k, v in (req.get("headers") or {}).items():
        if k.lower() in ("cookie", "csrf-token", "x-li-track", "x-restli-protocol-version", "accept", "user-agent"):
            lines.append(f"-H '{k}: {v}'")
    if req.get("postData"):
        lines.append(f"--data-raw '{req['postData']}'")
    (out / "curl.txt").write_text(" ".join(lines) + "\n", encoding="utf-8")

    meta_out = [
        {k: v for k, v in r["request"].items() if k != "headers"} | {"headers": r["request"].get("headers", {})}
        for r in responses
    ]
    (out / "requests.json").write_text(json.dumps(meta_out, indent=2), encoding="utf-8")

    print(f"\n✔ captured {len(responses)} voyager responses, {len(saved_pages)} saved pages")
    print(f"✔ feed request → {out / 'curl.txt'}")
    print(f"  {req['method']} {req['url'][:100]}…")
    cdp.close()


if __name__ == "__main__":
    main()
