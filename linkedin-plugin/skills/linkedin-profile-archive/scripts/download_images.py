#!/usr/bin/env python3
"""
download_images.py — Download LinkedIn post images THROUGH the logged-in browser
(CDP), because media.licdn.com 403s any non-browser HTTP client (Cloudflare TLS
fingerprinting), even with valid cookies.

How it works
------------
For each batch of URLs it creates <img> elements inside the page (the browser
attaches cookies + TLS identity automatically), captures the network responses
via CDP, and saves the binary bodies (base64 from Network.getResponseBody).

Resume: files that already exist in --dir are skipped, so re-running after an
interruption continues where it stopped. The WebSocket reconnects on drops.

Usage
-----
    python download_images.py --images images.json --dir out/images --port 9222

images.json is a list of {"url": "...", "file": "0001-01.jpg"}.
"""

from __future__ import annotations

import argparse
import base64
import json
import time
from pathlib import Path

import websocket
import urllib.request


def connect_page(port: int) -> websocket.WebSocket:
    tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5))
    pages = [t for t in tabs if t["type"] == "page"]
    if not pages:
        raise SystemExit("✗ no page tabs open in the browser")
    return websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=90, suppress_origin=True)

SCRIPT_LINKEDIN_ORIGIN = ("https://www.linkedin.com",)

def ensure_linkedin_origin(cdp: CDPPage, port: int):
    """Make sure the active page is on www.linkedin.com so image <img> loads carry
    the right Origin/CORS context (chrome:// pages drop the requests)."""
    res = cdp.send("Runtime.evaluate", {"expression": "location.origin", "returnByValue": True}, timeout=10)
    origin = (res.get("result", {}) or {}).get("value", "")
    if origin != "https://www.linkedin.com":
        # navigate an existing LinkedIn tab, else navigate current
        tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5))
        li = [t for t in tabs if t["type"] == "page" and t.get("url", "").startswith("https://www.linkedin.com")]
        if li:
            cdp.send("Page.navigate", {"url": li[0]["url"]}, timeout=30)
        else:
            cdp.send("Page.navigate", {"url": "https://www.linkedin.com/"}, timeout=30)
        time.sleep(3)
        print("  → set page origin to www.linkedin.com")


class CDPPage:
    def __init__(self, ws: websocket.WebSocket):
        self.ws = ws
        self._id = 0
        self._events: list[dict] = []

    def send(self, method: str, params: dict, timeout: float = 60) -> dict:
        self._id += 1
        mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.ws.settimeout(max(0.5, deadline - time.time()))
            try:
                raw = self.ws.recv()
            except websocket.WebSocketTimeoutException:
                continue
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", "replace")
            msg = json.loads(raw)
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"CDP {method}: {msg['error']}")
                return msg.get("result", {})
            if "method" in msg:
                self._events.append(msg)
        raise TimeoutError(f"CDP {method} timed out")

    def drain(self, method: str) -> list[dict]:
        out = [ev for ev in self._events if ev.get("method") == method]
        self._events = [ev for ev in self._events if ev.get("method") != method]
        return out


def fetch_batch(cdp: CDPPage, batch: list[dict], timeout: float = 20) -> dict[str, bytes]:
    """Load the batch URLs as <img> in the page and collect binary bodies.
    Phase 1: continuous recv loop collects {url: requestId} from network events.
    Phase 2: fetch each body via Network.getResponseBody (send() drains cleanly)."""
    js = ";".join(f"(new Image()).src={json.dumps(j['url'])};" for j in batch)
    cdp.send("Runtime.evaluate", {"expression": js}, timeout=15)
    url_rid: dict[str, str] = {}
    done_urls: set[str] = set()
    target_prefixes = sorted({j["url"][:50] for j in batch}, key=len, reverse=True)
    deadline = time.time() + timeout
    loaded: set[str] = set()
    while time.time() < deadline and len(loaded) < len(batch):
        remain = deadline - time.time()
        if remain <= 0:
            break
        cdp.ws.settimeout(min(1.0, remain))
        try:
            raw = cdp.ws.recv()
        except websocket.WebSocketTimeoutException:
            continue
        except (ConnectionError, OSError):
            break
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", "replace")
        try:
            msg = json.loads(raw)
        except Exception:
            continue
        if msg.get("id"):
            continue
        method = msg.get("method")
        p = msg.get("params", {})
        if method == "Network.responseReceived":
            url = p["response"]["url"]
            if any(url.startswith(pre) for pre in target_prefixes):
                rid = p["requestId"]
                url_rid[url] = rid
                if p["response"]["status"] not in (200,):
                    done_urls.add(url)  # treat non-200 as terminal/not downloadable
        elif method == "Network.loadingFinished":
            rid = p["requestId"]
            for u, r in list(url_rid.items()):
                if r == rid:
                    loaded.add(u)
    # Phase 2: fetch bodies
    bodies: dict[str, bytes] = {}
    for url in list(url_rid):
        try:
            res = cdp.send("Network.getResponseBody", {"requestId": url_rid[url]}, timeout=15)
            body = res.get("body", "")
            bodies[url] = base64.b64decode(body) if res.get("base64Encoded") else body.encode("utf-8", "replace")
        except Exception:
            continue
    return bodies


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", required=True, help="JSON list of {url, file}")
    ap.add_argument("--dir", required=True, help="destination directory")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--batch", type=int, default=6)
    ap.add_argument("--timeout", type=float, default=20, help="seconds to wait per batch")
    args = ap.parse_args()

    jobs = json.loads(Path(args.images).read_text(encoding="utf-8"))
    out = Path(args.dir)
    out.mkdir(parents=True, exist_ok=True)

    pending = [j for j in jobs if not (out / j["file"]).exists()]
    print(f"✔ {len(jobs)} images in manifest, {len(jobs) - len(pending)} already downloaded, {len(pending)} pending")

    failed: list[dict] = []
    done = 0
    ws = None

    while pending:
        try:
            if ws is None:
                ws = connect_page(args.port)
                cdp = CDPPage(ws)
                cdp.send("Network.enable", {})
                cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
                cdp.send("Page.enable", {})
                ensure_linkedin_origin(cdp, args.port)
                print(f"✔ connected (batch {args.batch})")
            batch = pending[: args.batch]
            pending = pending[args.batch :]
            bodies = fetch_batch(cdp, batch, args.timeout)
            for j in batch:
                data = bodies.get(j["url"])
                if data:
                    (out / j["file"]).write_bytes(data)
                    done += 1
                    print(f"  ✔ {j['file']} ({len(data)//1024} KB)")
                else:
                    failed.append(j)
            if len(batch) == len(bodies) and batch:
                time.sleep(0.3)
        except (ConnectionResetError, ConnectionError, websocket.WebSocketException, OSError) as e:
            print(f"  ⚠ connection lost ({e}) — reconnecting…")
            try:
                ws.close()
            except Exception:
                pass
            ws = None
            pending = batch + pending  # re-queue current batch
            time.sleep(3)

    # one retry pass for failures
    if failed:
        print(f"  … retrying {len(failed)} failures")
        time.sleep(2)
        for j in failed:
            try:
                if ws is None:
                    ws = connect_page(args.port)
                    cdp = CDPPage(ws)
                    cdp.send("Network.enable", {})
                    cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
                    cdp.send("Page.enable", {})
                    ensure_linkedin_origin(cdp, args.port)
                bodies = fetch_batch(cdp, [j], args.timeout)
                data = bodies.get(j["url"])
                if data:
                    (out / j["file"]).write_bytes(data)
                    done += 1
                    print(f"  ✔ (retry) {j['file']} ({len(data)//1024} KB)")
            except Exception as e:
                print(f"  ⚠ retry failed for {j['file']}: {e}")
    if ws:
        try:
            ws.close()
        except Exception:
            pass

    total = len(jobs)
    print(f"\n=== done: {done}/{total} images → {out}")
    if done < total:
        missing = [j["file"] for j in jobs if not (out / j["file"]).exists()]
        print(f"⚠ {len(missing)} missing (re-run to retry): {missing[:10]}")


if __name__ == "__main__":
    main()
