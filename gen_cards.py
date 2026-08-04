#!/usr/bin/env python3
"""Build flow.svg and dsa.svg — custom animated cards for the profile README.

Both are plain SVG with CSS keyframes, committed straight into the repo. No
external service, no GitHub Action, no API call. They render the moment you push.

Run:  python3 gen_cards.py
"""

import xml.etree.ElementTree as ET

# ---------- shared palette (matches whoami.svg exactly) ----------
BG, BAR, BORDER = "#0d1117", "#161b22", "#30363d"
FG, MUTED, DIM = "#e6edf3", "#8b949e", "#6e7681"
TRACK = "#21262d"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
ORANGE = "#f0883e"

MONO = ("'JetBrains Mono','DejaVu Sans Mono','SFMono-Regular',"
        "Consolas,monospace")


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ══════════════════════════════════════════════════════════════════
#  CARD 1 — request lifecycle through the stack
# ══════════════════════════════════════════════════════════════════
def build_flow(path="flow.svg"):
    W = 580
    NODE_W, NODE_H = 76, 58
    GAP = 45
    X0, NODE_Y = 10, 56

    nodes = [
        ("Client", "browser", DIM),
        ("React", "Next.js", "#087EA4"),
        ("API", "Node · TS", "#5FA04E"),
        ("Cache", "Redis", "#FF4438"),
        ("DB", "Postgres", "#4169E1"),
    ]

    xs = [X0 + i * (NODE_W + GAP) for i in range(len(nodes))]
    H = 186

    HOP = 0.52          # seconds per hop
    STEP = 0.60         # start-to-start spacing
    PAUSE = 1.1
    TOTAL = STEP * (len(nodes) - 1) + HOP + PAUSE

    def pct(t):
        return round(t / TOTAL * 100, 3)

    css = [
        f"text{{font-family:{MONO}}}",
        # packet hops between nodes
    ]
    for i in range(len(nodes) - 1):
        start = xs[i] + NODE_W
        end = xs[i + 1]
        s, e = i * STEP, i * STEP + HOP
        css.append(
            f".p{i}{{opacity:0;animation:hop{i} {TOTAL:.2f}s linear infinite}}"
        )
        css.append(
            "@keyframes hop%d{0%%{opacity:0;transform:translateX(%dpx)}"
            "%s%%{opacity:0;transform:translateX(%dpx)}"
            "%s%%{opacity:1;transform:translateX(%dpx)}"
            "%s%%{opacity:1;transform:translateX(%dpx)}"
            "%s%%{opacity:0;transform:translateX(%dpx)}"
            "100%%{opacity:0;transform:translateX(%dpx)}}"
            % (i, start,
               max(0.0, pct(s) - 0.01), start,
               pct(s), start,
               pct(e), end,
               min(100.0, pct(e) + 0.01), end,
               end)
        )
        # connector line fills as the packet crosses it
        css.append(
            f".w{i}{{stroke-dasharray:{GAP};stroke-dashoffset:{GAP};"
            f"animation:wire{i} {TOTAL:.2f}s linear infinite}}"
        )
        css.append(
            "@keyframes wire%d{0%%{stroke-dashoffset:%d}"
            "%s%%{stroke-dashoffset:%d}%s%%{stroke-dashoffset:0}"
            "%s%%{stroke-dashoffset:0}100%%{stroke-dashoffset:0}}"
            % (i, GAP, pct(s), GAP, pct(e), pct(TOTAL - 0.15))
        )

    # each node lights up when the packet arrives
    for i in range(len(nodes)):
        arrive = max(0.0, i * STEP - 0.04)
        css.append(f".n{i}{{animation:lit{i} {TOTAL:.2f}s linear infinite}}")
        css.append(
            "@keyframes lit%d{0%%{opacity:.55}%s%%{opacity:.55}"
            "%s%%{opacity:1}%s%%{opacity:1}100%%{opacity:.55}}"
            % (i, max(0.0, pct(arrive) - 0.01), pct(arrive),
               pct(TOTAL - 0.25))
        )

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Request lifecycle: client to React to Node API to Redis '
         f'cache to Postgres, deployed on AWS">']
    o.append("<style>" + "".join(css) + "</style>")
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" '
             f'fill="{BG}" stroke="{BORDER}"/>')
    o.append(f'<text x="20" y="30" fill="{FG}" font-size="13" '
             f'font-weight="600">request lifecycle</text>')
    o.append(f'<text x="{W-20}" y="30" fill="{DIM}" font-size="11" '
             f'text-anchor="end">how I think about a stack</text>')

    # connectors + packets
    cy = NODE_Y + NODE_H / 2
    for i in range(len(nodes) - 1):
        x1 = xs[i] + NODE_W
        x2 = xs[i + 1]
        o.append(f'<line x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" '
                 f'stroke="{TRACK}" stroke-width="2"/>')
        o.append(f'<line class="w{i}" x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" '
                 f'stroke="{ACCENT}" stroke-width="2"/>')

    # nodes
    for i, (name, sub, col) in enumerate(nodes):
        x = xs[i]
        o.append(f'<g class="n{i}">')
        o.append(f'<rect x="{x}" y="{NODE_Y}" width="{NODE_W}" height="{NODE_H}" '
                 f'rx="7" fill="{BAR}" stroke="{col}" stroke-width="1.5"/>')
        o.append(f'<text x="{x + NODE_W/2}" y="{NODE_Y + 24}" fill="{FG}" '
                 f'font-size="12" font-weight="600" text-anchor="middle">'
                 f'{esc(name)}</text>')
        o.append(f'<text x="{x + NODE_W/2}" y="{NODE_Y + 41}" fill="{DIM}" '
                 f'font-size="9.5" text-anchor="middle">{esc(sub)}</text>')
        o.append("</g>")

    # travelling packets, drawn last so they sit on top
    for i in range(len(nodes) - 1):
        o.append(f'<circle class="p{i}" cx="0" cy="{cy}" r="3.5" '
                 f'fill="{ACCENT}"/>')

    # infra band
    by = 140
    o.append(f'<rect x="10" y="{by}" width="{W-20}" height="34" rx="7" '
             f'fill="{BAR}" stroke="{BORDER}"/>')
    o.append(f'<text x="{W/2}" y="{by + 21}" fill="{MUTED}" font-size="10.5" '
             f'text-anchor="middle">AWS  ·  Docker  ·  GitHub Actions  ·  '
             f'JWT / OAuth 2.0</text>')

    o.append("</svg>")
    svg = "".join(o)
    open(path, "w", encoding="utf-8").write(svg)
    return path, svg, W, H


# ══════════════════════════════════════════════════════════════════
#  CARD 2 — DSA pattern coverage
# ══════════════════════════════════════════════════════════════════
def build_dsa(path="dsa.svg"):
    W = 580
    rows = [
        ("Arrays & Hashing",            1.00, GREEN),
        ("Two Pointers / Sliding Win",  1.00, GREEN),
        ("Binary Search",               1.00, GREEN),
        ("Trees & BST (iterative)",     1.00, GREEN),
        ("Graphs — BFS / DFS / Topo",   0.55, ACCENT),
        ("Dynamic Programming",         0.40, ACCENT),
        ("Heaps / Intervals",           0.12, ORANGE),
        ("Tries & Union-Find",          0.10, ORANGE),
    ]

    LX, LW = 20, 218        # label column
    BX = 250                # bar start
    BW = W - BX - 20        # bar width
    TOP = 58
    RH = 26
    H = TOP + len(rows) * RH + 34

    css = [f"text{{font-family:{MONO}}}"]
    for i, (_, frac, _) in enumerate(rows):
        w = BW * frac
        css.append(
            f".b{i}{{animation:g{i} .85s cubic-bezier(.4,0,.2,1) both;"
            f"animation-delay:{0.07 * i:.2f}s}}"
        )
        css.append("@keyframes g%d{from{width:0}to{width:%.1fpx}}" % (i, w))

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="DSA pattern coverage across Neetcode 150">']
    o.append("<style>" + "".join(css) + "</style>")
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" '
             f'fill="{BG}" stroke="{BORDER}"/>')

    o.append(f'<text x="20" y="30" fill="{FG}" font-size="13" '
             f'font-weight="600">pattern coverage</text>')
    o.append(f'<text x="{W-20}" y="30" fill="{DIM}" font-size="11" '
             f'text-anchor="end">Blind 75 → Neetcode 150</text>')
    o.append(f'<line x1="20" y1="42" x2="{W-20}" y2="42" stroke="{BORDER}"/>')

    for i, (label, frac, col) in enumerate(rows):
        y = TOP + i * RH
        o.append(f'<text x="{LX}" y="{y + 4}" fill="{MUTED}" font-size="11">'
                 f'{esc(label)}</text>')
        o.append(f'<rect x="{BX}" y="{y - 5}" width="{BW}" height="8" rx="4" '
                 f'fill="{TRACK}"/>')
        o.append(f'<rect class="b{i}" x="{BX}" y="{y - 5}" '
                 f'width="{BW * frac:.1f}" height="8" rx="4" fill="{col}"/>')

    ly = H - 14
    legend = [("shipped", GREEN), ("in progress", ACCENT), ("queued", ORANGE)]
    lx = 20
    for name, col in legend:
        o.append(f'<circle cx="{lx + 4}" cy="{ly - 4}" r="4" fill="{col}"/>')
        o.append(f'<text x="{lx + 14}" y="{ly}" fill="{DIM}" font-size="10">'
                 f'{name}</text>')
        lx += 22 + len(name) * 6.2
    o.append("</svg>")

    svg = "".join(o)
    open(path, "w", encoding="utf-8").write(svg)
    return path, svg, W, H


# ══════════════════════════════════════════════════════════════════
def verify(path, W, H):
    """Fail loudly if anything sits outside the canvas."""
    ns = "{http://www.w3.org/2000/svg}"
    root = ET.parse(path).getroot()
    bad = []

    def n(e, k, d=0.0):
        try:
            return float(e.get(k))
        except (TypeError, ValueError):
            return d

    for e in root.iter():
        t = e.tag.replace(ns, "")
        if t == "rect":
            x, y, w, h = n(e, "x"), n(e, "y"), n(e, "width"), n(e, "height")
            if x < -0.6 or y < -0.6 or x + w > W + 0.6 or y + h > H + 0.6:
                bad.append(f"rect {x},{y} {w}x{h}")
        elif t == "text":
            x, y = n(e, "x"), n(e, "y")
            fs = n(e, "font-size", 12)
            txt = "".join(e.itertext())
            wpx = len(txt) * fs * 0.62
            a = e.get("text-anchor", "start")
            left = x - wpx if a == "end" else (x - wpx / 2 if a == "middle" else x)
            if left < -0.6 or left + wpx > W + 0.6 or y > H:
                bad.append(f"text {txt[:28]!r} {left:.0f}..{left+wpx:.0f}")
        elif t == "line":
            for xk in ("x1", "x2"):
                if not (-0.6 <= n(e, xk) <= W + 0.6):
                    bad.append(f"line {xk}={n(e, xk)}")
    return bad


if __name__ == "__main__":
    for builder in (build_flow, build_dsa):
        p, svg, W, H = builder()
        issues = verify(p, W, H)
        status = "OK" if not issues else f"{len(issues)} ISSUES"
        print(f"{p:12s} {W}x{H}  {len(svg):5d} bytes  {status}")
        for i in issues:
            print("   -", i)
