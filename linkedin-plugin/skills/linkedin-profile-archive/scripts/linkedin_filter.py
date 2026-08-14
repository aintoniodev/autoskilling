#!/usr/bin/env python3
"""
linkedin_filter.py — Filter an archived LinkedIn profile (linkedin_archive.py output)
to a date range, keeping EVERY post field intact (full text, metrics, all images).
Writes a new archive folder with its own index.json, posts/ and images/ (files copied).

Usage
-----
    python linkedin_filter.py --index output/<slug>/index.json \
        --from 2024-08-15 --to 2026-08-14 --out output/<slug>-2y

    # last N years relative to today:
    python linkedin_filter.py --index output/<slug>/index.json --years 2 --out output/<slug>-2y

The filter is purely date-based: no field is dropped or truncated ("sin filtrar info").
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index", required=True, help="source index.json")
    ap.add_argument("--out", required=True, help="destination folder")
    ap.add_argument("--from", dest="date_from", help="inclusive start YYYY-MM-DD")
    ap.add_argument("--to", dest="date_to", help="inclusive end YYYY-MM-DD")
    ap.add_argument("--years", type=float, help="alternative: last N years up to today")
    args = ap.parse_args()

    if args.years:
        today = datetime.now().date()
        args.date_to = args.date_to or today.isoformat()
        args.date_from = (today - timedelta(days=365 * args.years)).isoformat()
    if not args.date_from or not args.date_to:
        ap.error("pass --from/--to or --years")
    d_from = datetime.strptime(args.date_from, "%Y-%m-%d").date()
    d_to = datetime.strptime(args.date_to, "%Y-%m-%d").date()

    src = Path(args.index).parent
    posts = json.loads(Path(args.index).read_text(encoding="utf-8"))

    kept = []
    dropped = 0
    for p in posts:
        d = (p.get("date") or "")[:10]
        try:
            pd = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            dropped += 1  # unknown date: keep? no — date unknown can't be filtered
            continue
        if d_from <= pd <= d_to:
            kept.append(p)
        else:
            dropped += 1

    if not kept:
        raise SystemExit("✗ no posts in range")

    out = Path(args.out)
    posts_dir = out / "posts"
    images_dir = out / "images"
    posts_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for p in kept:
        # copy each post markdown (find by num prefix in source posts/)
        num = p.get("num", "")
        matches = list((src / "posts").glob(f"{num}-*.md"))
        for m in matches:
            shutil.copy2(m, posts_dir / m.name)
        for img in p.get("images", []):
            f = src / "images" / img
            if f.exists():
                shutil.copy2(f, images_dir / img)
                copied += 1

    (out / "index.json").write_text(
        json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # refresh image manifest from the source manifest (keeps original signed URLs)
    src_manifest = {}
    src_mf_path = src / "images.json"
    if src_mf_path.exists():
        for m in json.loads(src_mf_path.read_text(encoding="utf-8")):
            src_manifest[m["file"]] = m.get("url", "")
    manifest = [
        {"url": src_manifest.get(img, ""), "file": img}
        for img in sorted(im for p in kept for im in p.get("images", []))
    ]
    (out / "images.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    total_imgs = sum(len(p.get("images", [])) for p in kept)
    print(f"✔ kept {len(kept)}/{len(posts)} posts ({dropped} dropped) — {args.date_from} → {args.date_to}")
    print(f"  images referenced: {total_imgs}, copied: {copied}")
    print(f"  → {out}")


if __name__ == "__main__":
    main()
