#!/usr/bin/env python3
"""Generate a LeetCode stats card as a local SVG.

Queries LeetCode's public GraphQL endpoint and renders a card styled to match
whoami.svg. Output is a committed file in the repo, so rendering never depends
on a third-party image service being up.

Usage:
    python3 gen_leetcode.py                    # live fetch
    python3 gen_leetcode.py --mock             # render with fake data (offline)
    python3 gen_leetcode.py --user someone     # override handle

Stdlib only, so the GitHub Action needs no pip install.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

USER = "surajmishragemini"
ENDPOINT = "https://leetcode.com/graphql"
OUT = "leetcode.svg"

# ---------- palette: identical to whoami.svg ----------
BG, BAR, BORDER = "#0d1117", "#161b22", "#30363d"
FG, MUTED, DIM = "#e6edf3", "#8b949e", "#6e7681"
EASY, MED, HARD = "#00b8a3", "#ffc01e", "#ff375f"
TRACK = "#21262d"
ACCENT = "#58a6ff"

QUERY = """
query userProfile($username: String!) {
  matchedUser(username: $username) {
    username
    profile { ranking }
    submitStatsGlobal { acSubmissionNum { difficulty count } }
  }
  allQuestionsCount { difficulty count }
}
"""


def fetch(username):
    """Return (solved, totals, ranking). Raises on failure."""
    body = json.dumps({
        "query": QUERY,
        "variables": {"username": username},
    }).encode()

    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "User-Agent": "Mozilla/5.0 (compatible; profile-readme-card/1.0)",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        payload = json.loads(r.read().decode())

    if payload.get("errors"):
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")

    user = payload["data"]["matchedUser"]
    if user is None:
        raise RuntimeError(f"user '{username}' not found")

    solved = {d["difficulty"]: d["count"]
              for d in user["submitStatsGlobal"]["acSubmissionNum"]}
    totals = {d["difficulty"]: d["count"]
              for d in payload["data"]["allQuestionsCount"]}
    ranking = user["profile"].get("ranking")
    return solved, totals, ranking


def mock():
    solved = {"All": 601, "Easy": 338, "Medium": 240, "Hard": 23}
    totals = {"All": 2168, "Easy": 871, "Medium": 558, "Hard": 739}
    return solved, totals, 412873


def render(solved, totals, ranking, username):
    W = 580
    H = 196
    total_solved = solved.get("All", 0)

    parts = [
        ("Easy", solved.get("Easy", 0), totals.get("Easy", 1), EASY),
        ("Medium", solved.get("Medium", 0), totals.get("Medium", 1), MED),
        ("Hard", solved.get("Hard", 0), totals.get("Hard", 1), HARD),
    ]

    s = []
    s.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="LeetCode: {total_solved} problems solved by {username}">'
    )

    s.append(
        "<style>"
        "text{font-family:'JetBrains Mono','DejaVu Sans Mono','SFMono-Regular',"
        "Consolas,monospace}"
        "@keyframes grow{from{stroke-dashoffset:var(--c)}to{stroke-dashoffset:var(--o)}}"
        "@keyframes fill{from{width:0}}"
        ".arc{animation:grow 1.1s cubic-bezier(.4,0,.2,1) both}"
        ".bar{animation:fill 1.1s cubic-bezier(.4,0,.2,1) both}"
        "</style>"
    )

    # frame
    s.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" '
             f'fill="{BG}" stroke="{BORDER}"/>')

    # header
    s.append(f'<text x="24" y="34" fill="{FG}" font-size="14" font-weight="600">'
             f'LeetCode</text>')
    s.append(f'<text x="102" y="34" fill="{DIM}" font-size="12">{username}</text>')
    if ranking:
        s.append(f'<text x="{W-24}" y="34" fill="{ACCENT}" font-size="12" '
                 f'text-anchor="end">rank #{ranking:,}</text>')
    s.append(f'<line x1="24" y1="48" x2="{W-24}" y2="48" stroke="{BORDER}"/>')

    # ---------- donut ----------
    cx, cy, r = 84, 122, 42
    C = 2 * 3.141592653589793 * r
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{TRACK}" '
             f'stroke-width="9"/>')

    # stacked arcs, each proportional to its share of solved problems
    offset = 0.0
    delay = 0.0
    for _, count, _, col in parts:
        if total_solved <= 0 or count <= 0:
            continue
        frac = count / total_solved
        seg = C * frac
        dash_off = C - offset
        s.append(
            f'<circle class="arc" cx="{cx}" cy="{cy}" r="{r}" fill="none" '
            f'stroke="{col}" stroke-width="9" stroke-linecap="butt" '
            f'stroke-dasharray="{seg:.2f} {C - seg:.2f}" '
            f'stroke-dashoffset="{dash_off:.2f}" '
            f'style="--c:{C:.2f};--o:{dash_off:.2f};'
            f'animation-delay:{delay:.2f}s" '
            f'transform="rotate(-90 {cx} {cy})"/>'
        )
        offset += seg
        delay += 0.14

    s.append(f'<text x="{cx}" y="{cy - 2}" fill="{FG}" font-size="24" '
             f'font-weight="700" text-anchor="middle">{total_solved}</text>')
    s.append(f'<text x="{cx}" y="{cy + 17}" fill="{DIM}" font-size="10" '
             f'text-anchor="middle">solved</text>')

    # ---------- difficulty bars ----------
    bx, bw = 168, 388
    by = 78
    for i, (label, count, total, col) in enumerate(parts):
        y = by + i * 34
        pct = (count / total) if total else 0.0
        fw = max(2.0, bw * min(pct, 1.0))
        s.append(f'<text x="{bx}" y="{y}" fill="{MUTED}" font-size="12">{label}</text>')
        s.append(f'<text x="{bx + bw}" y="{y}" fill="{FG}" font-size="12" '
                 f'text-anchor="end">{count} <tspan fill="{DIM}">/ {total}</tspan></text>')
        s.append(f'<rect x="{bx}" y="{y + 8}" width="{bw}" height="6" rx="3" '
                 f'fill="{TRACK}"/>')
        s.append(f'<rect class="bar" x="{bx}" y="{y + 8}" width="{fw:.1f}" '
                 f'height="6" rx="3" fill="{col}" '
                 f'style="animation-delay:{0.14 * i:.2f}s"/>')

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    s.append(f'<text x="{W-24}" y="{H-14}" fill="{DIM}" font-size="9" '
             f'text-anchor="end">updated {stamp}</text>')

    s.append("</svg>")
    return "".join(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true", help="render offline with fake data")
    ap.add_argument("--user", default=USER)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()

    if a.mock:
        solved, totals, ranking = mock()
        print("rendering with mock data")
    else:
        try:
            solved, totals, ranking = fetch(a.user)
        except (urllib.error.URLError, RuntimeError, KeyError, TimeoutError) as e:
            # Never overwrite a good card with a broken one. Exiting non-zero
            # fails the Action loudly while the last committed SVG stays live.
            print(f"fetch failed: {e}", file=sys.stderr)
            return 1

    svg = render(solved, totals, ranking, a.user)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"wrote {a.out}  ({len(svg)} bytes)  "
          f"solved={solved.get('All')} rank={ranking}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
