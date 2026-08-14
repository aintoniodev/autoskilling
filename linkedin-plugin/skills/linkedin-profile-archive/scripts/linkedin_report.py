#!/usr/bin/env python3
"""
linkedin_report.py — Summarize an archived LinkedIn profile (from linkedin_archive output).

Reads out/index.json and prints a compact analytical summary plus optional markdown report:
    - total posts, date range, posting cadence (posts/month, best/worst day)
    - top posts by reactions/comments/engagement
    - engagement rate over time
    - most common topics (by keyword frequency in post text)

Usage
-----
    python linkedin_report.py --index output/<slug>/index.json [--md output/<slug>/REPORT.md]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

STOP = set(
    "de la que en y a los del se las un por con no una su para es al lo como más o pero sus le ha sino "
    "si ya este porque esta entre cuando muy sin sobre también me hasta hay donde quien desde todo nos "
    "durante todos uno les ni contra otros ese eso ante ellos e esto mí antes algunos qué unos yo otro "
    "otras otra él tanto esa estos mucho quienes nada muchos cual poco ella estar estas algunas algo "
    "nosotros mi mis tú te ti tu tus ellas nosotras vosotros vosotras os mío mía míos mías tuyo tuya "
    "suyos suya nuestro nuestra nuestros nuestras vuestro vuestra vuestros vuestras esos esas estoy "
    "estás está estamos estáis están esté estés estemos estéis estén estaré esta".split()
)


def metric(post: dict, key: str) -> int:
    m = post.get("metrics", {}) or {}
    if key in m:
        return int(m[key])
    # aggregate keys
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index", required=True, help="index.json path")
    ap.add_argument("--md", help="write a markdown report to this file")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    posts = json.loads(Path(args.index).read_text(encoding="utf-8"))
    if not posts:
        print("no posts")
        return

    dates = []
    for p in posts:
        d = p.get("date", "")
        m = re.search(r"(\d{4}-\d{2}-\d{2})", d)
        if m:
            dates.append(m.group(1))
    dates.sort()
    first = dates[0] if dates else "?"
    last = dates[-1] if dates else "?"

    per_month = Counter(d[:7] for d in dates)
    months = sorted(per_month)
    monthly = [int(per_month[m]) for m in months]

    def eng(post) -> float:
        like = metric(post, "likes")
        com = metric(post, "comments")
        rep = metric(post, "reposts") + metric(post, "shares")
        return like + com * 2 + rep * 3

    posts_sorted = sorted(posts, key=eng, reverse=True)

    # cadence
    total_months = max(1, (len(months) or 1))
    total_posts = len(posts)
    avg_per_month = total_posts / total_months

    # topics
    words = Counter()
    for p in posts:
        t = (p.get("text") or "").lower()
        for w in re.findall(r"[a-záéíóúñü]+", t):
            w2 = w.rstrip("s")  # crude plural fold
            if len(w2) > 3 and w not in STOP and w2 not in STOP:
                words[w2] += 1

    with_img = sum(1 for p in posts if p.get("images"))
    total_eng = sum(eng(p) for p in posts)
    total_reactions = sum(metric(p, "likes") for p in posts)

    lines = []
    lines.append(f"# LinkedIn report — {args.index}")
    lines.append("")
    lines.append(f"- **Posts:** {total_posts}")
    lines.append(f"- **Date range:** {first} → {last}")
    lines.append(f"- **Avg / month:** {avg_per_month:.1f}")
    lines.append(f"- **With images:** {with_img} ({100*with_img//total_posts}%)")
    lines.append(f"- **Total reactions:** {total_reactions}  **Total engagement score:** {total_eng}")
    lines.append("")
    lines.append("## Top posts by engagement")
    lines.append("")
    lines.append("| # | date | likes | comments | reposts | eng | first 60 chars |")
    lines.append("|---|---|---|---|---|---|---|")
    for p in posts_sorted[: args.top]:
        t = (p.get("text") or "").replace("|", "/").replace("\n", " ")[:60]
        lines.append(
            f"| {p.get('num','')} | {(p.get('date') or '?')[:10]} | {metric(p,'likes')} | "
            f"{metric(p,'comments')} | {metric(p,'reposts')+metric(p,'shares')} | {eng(p):.0f} | {t} |"
        )
    lines.append("")
    lines.append("## Cadence (posts / month)")
    lines.append("")
    lines.append("| month | posts |")
    lines.append("|---|---|")
    for m in months:
        lines.append(f"| {m} | {per_month[m]} |")
    lines.append("")
    lines.append("## Top 30 keywords")
    lines.append("")
    lines.append("| word | count |")
    lines.append("|---|---|")
    for w, c in words.most_common(30):
        lines.append(f"| {w} | {c} |")
    lines.append("")

    report = "\n".join(lines)
    print("\n".join(lines[:40]))
    print(f"\n… {len(lines)} lines total")

    if args.md:
        Path(args.md).write_text(report, encoding="utf-8")
        print(f"✔ wrote {args.md}")


if __name__ == "__main__":
    main()
