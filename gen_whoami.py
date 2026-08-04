#!/usr/bin/env python3
"""Generate an animated terminal SVG for a GitHub profile README.

Pure CSS keyframes (no JS, no SMIL) so it animates when GitHub loads it
via <img>. Commands "type" via an animated clip rect; output lines fade
in instantly, which is how a real shell behaves.
"""

# ---------- palette (GitHub dark) ----------
BG        = "#0d1117"
BAR       = "#161b22"
BORDER    = "#30363d"
FG        = "#e6edf3"
MUTED     = "#8b949e"
DIM       = "#6e7681"
GREEN     = "#3fb950"
BLUE      = "#58a6ff"
ORANGE    = "#f0883e"
CYAN      = "#39c5cf"

# ---------- geometry ----------
FS       = 14.0          # font-size
ADV      = FS * 0.6      # monospace advance width
PAD_X    = 24
BAR_H    = 38
TOP      = BAR_H + 26
LH       = 25.0          # line height
WIDTH    = 580
PROMPT   = "$ "

# ---------- content ----------
# ('cmd', text)                  -> types out after a green "$ "
# ('out', [(text, color)])       -> appears instantly
# ('gap', None)                  -> vertical breathing room
LINES = [
    ("cmd", "whoami"),
    ("out", [("Suraj Mishra", FG), ("  —  Software Engineer", MUTED)]),
    ("out", [("M.S. Computer Science, Northeastern University", DIM)]),
    ("gap", None),

    ("cmd", "cat stack.txt"),
    ("out", [("C++   TypeScript   Java   Node.js   React   PostgreSQL   AWS", BLUE)]),
    ("gap", None),

    ("cmd", "./status --now"),
    ("out", [("building   ", CYAN), ("Threadwire — RAG pipeline over manufacturing data", MUTED)]),
    ("out", [("grinding   ", CYAN), ("Neetcode 150  ·  system design mocks", MUTED)]),
    ("out", [("open to    ", CYAN), ("Backend  ·  Frontend  ·  Full-Stack SWE", MUTED)]),
    ("gap", None),

    ("cmd", "echo $PRINCIPLE"),
    ("out", [('"Correct, then fast, then measured."', ORANGE)]),
    ("gap", None),
    ("prompt", None),   # bare prompt + persistent blinking cursor
]

# ---------- timeline ----------
CPS       = 0.052   # seconds per typed character
OUT_DUR   = 0.16
GAP_CMD   = 0.34
GAP_OUT   = 0.16
GAP_BLANK = 0.30
HOLD      = 6.5     # dwell on the finished screen
FADE      = 1.2     # fade out before looping

t = 0.35            # small lead-in
events = []         # (kind, index, start, end, payload)
y = TOP

for i, (kind, payload) in enumerate(LINES):
    if kind == "gap":
        t += GAP_BLANK
        y += LH * 0.55
        continue

    if kind == "cmd":
        dur = max(0.30, len(payload) * CPS)
        events.append(dict(kind="cmd", i=i, y=y, start=t, end=t + dur, text=payload))
        t += dur + GAP_CMD

    elif kind == "out":
        events.append(dict(kind="out", i=i, y=y, start=t, end=t + OUT_DUR, segs=payload))
        t += OUT_DUR + GAP_OUT

    elif kind == "prompt":
        events.append(dict(kind="prompt", i=i, y=y, start=t, end=t + 0.2))
        t += 0.2

    y += LH

TYPE_END = t
TOTAL    = TYPE_END + HOLD + FADE
HEIGHT   = int(y + 22)


def pct(seconds):
    return round(seconds / TOTAL * 100, 4)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


# ---------- build CSS ----------
css = [
    "text{font-family:'JetBrains Mono','DejaVu Sans Mono','SFMono-Regular',"
    f"Consolas,monospace;font-size:{FS}px;dominant-baseline:middle;"
    "white-space:pre}",
    ".sc{opacity:0;animation:screen %.3fs linear infinite}" % TOTAL,
    "@keyframes screen{0%%{opacity:0}%s{opacity:1}%s{opacity:1}%s{opacity:0}100%%{opacity:0}}"
    % (f"{pct(0.18)}%", f"{pct(TYPE_END + HOLD)}%", f"{pct(TOTAL - 0.05)}%"),
]

# per-command typing clip + travelling cursor
for e in events:
    if e["kind"] != "cmd":
        continue
    n = e["i"]
    x0 = PAD_X + len(PROMPT) * ADV
    w = len(e["text"]) * ADV
    s, en = pct(e["start"]), pct(e["end"])

    css.append(
        f"#clip{n} rect{{width:0px;animation:typ{n} {TOTAL:.3f}s steps({len(e['text'])},end) infinite}}"
    )
    css.append(
        "@keyframes typ%d{0%%{width:0px}%s%%{width:0px}%s%%{width:%.1fpx}"
        "100%%{width:%.1fpx}}" % (n, s, en, w, w)
    )
    # cursor rides the reveal edge, then vanishes
    css.append(f".cur{n}{{opacity:0;animation:cur{n} {TOTAL:.3f}s linear infinite}}")
    css.append(
        "@keyframes cur%d{0%%{opacity:0;transform:translateX(%.1fpx)}"
        "%s%%{opacity:0;transform:translateX(%.1fpx)}"
        "%s%%{opacity:1;transform:translateX(%.1fpx)}"
        "%s%%{opacity:1;transform:translateX(%.1fpx)}"
        "%s%%{opacity:0;transform:translateX(%.1fpx)}"
        "100%%{opacity:0;transform:translateX(%.1fpx)}}"
        % (n, x0,
           max(0.0, s - 0.01), x0,
           s, x0,
           en, x0 + w,
           min(100.0, en + 0.01), x0 + w,
           x0 + w)
    )

# output-line fade-ins
for e in events:
    if e["kind"] != "out":
        continue
    n, s, en = e["i"], pct(e["start"]), pct(e["end"])
    css.append(f".ln{n}{{opacity:0;animation:in{n} {TOTAL:.3f}s linear infinite}}")
    css.append(
        "@keyframes in%d{0%%{opacity:0}%s%%{opacity:0}%s%%{opacity:1}100%%{opacity:1}}"
        % (n, s, en)
    )

# final prompt gate + independent blink
pe = next(e for e in events if e["kind"] == "prompt")
css.append(f".pgate{{opacity:0;animation:pin {TOTAL:.3f}s linear infinite}}")
css.append(
    "@keyframes pin{0%%{opacity:0}%s%%{opacity:0}%s%%{opacity:1}100%%{opacity:1}}"
    % (pct(pe["start"]), pct(pe["end"]))
)
css.append("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}")
css.append(".blink{animation:blink 1.06s steps(1,end) infinite}")

# ---------- build body ----------
out = []
out.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
    f'aria-label="Animated terminal introducing Suraj Mishra, backend software engineer">'
)
out.append("<style>" + "".join(css) + "</style>")

# window chrome
out.append(f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="10" '
           f'fill="{BG}" stroke="{BORDER}"/>')
out.append(f'<path d="M0.5 10.5a10 10 0 0 1 10-10h{WIDTH-21}a10 10 0 0 1 10 10v{BAR_H-10}H0.5z" '
           f'fill="{BAR}"/>')
out.append(f'<line x1="0.5" y1="{BAR_H}" x2="{WIDTH-0.5}" y2="{BAR_H}" stroke="{BORDER}"/>')
for cx, col in ((22, "#ff5f57"), (42, "#febc2e"), (62, "#28c840")):
    out.append(f'<circle cx="{cx}" cy="{BAR_H/2}" r="6" fill="{col}"/>')
out.append(f'<text x="{WIDTH/2}" y="{BAR_H/2}" fill="{DIM}" font-size="12" '
           f'text-anchor="middle">suraj@dev — zsh</text>')

# clip paths for typing
out.append("<defs>")
for e in events:
    if e["kind"] == "cmd":
        x0 = PAD_X + len(PROMPT) * ADV
        fullw = len(e["text"]) * ADV
        out.append(f'<clipPath id="clip{e["i"]}"><rect x="{x0}" y="{e["y"]-11}" '
                   f'width="{fullw:.1f}" height="20"/></clipPath>')
out.append("</defs>")

out.append('<g class="sc">')
for e in events:
    y = e["y"]
    if e["kind"] == "cmd":
        n = e["i"]
        x0 = PAD_X + len(PROMPT) * ADV
        # prompt is revealed together with the cursor gate, so it appears
        # exactly when typing starts
        out.append(f'<text x="{PAD_X}" y="{y}" fill="{GREEN}" class="ln_p{n}">'
                   f'{esc(PROMPT.rstrip())}</text>')
        out.append(f'<g clip-path="url(#clip{n})"><text x="{x0}" y="{y}" fill="{FG}">'
                   f'{esc(e["text"])}</text></g>')
        out.append(f'<rect class="cur{n}" x="0" y="{y-9}" width="8" height="17" '
                   f'fill="{FG}" opacity="0"/>')
    elif e["kind"] == "out":
        n = e["i"]
        spans = []
        for text, col in e["segs"]:
            spans.append(f'<tspan fill="{col}">{esc(text)}</tspan>')
        out.append(f'<text x="{PAD_X}" y="{y}" class="ln{n}">{"".join(spans)}</text>')
    else:  # prompt
        out.append(f'<g class="pgate">')
        out.append(f'<text x="{PAD_X}" y="{y}" fill="{GREEN}">$</text>')
        out.append(f'<rect class="blink" x="{PAD_X + len(PROMPT)*ADV}" y="{y-9}" '
                   f'width="8" height="17" fill="{FG}" opacity="0.85"/>')
        out.append("</g>")
out.append("</g>")
out.append("</svg>")

svg = "".join(out)

# prompts for cmd lines need the same gate as their cursor; reuse the fade class
extra = []
for e in events:
    if e["kind"] == "cmd":
        n = e["i"]
        extra.append(f".ln_p{n}{{opacity:0;animation:in_p{n} {TOTAL:.3f}s linear infinite}}")
        extra.append(
            "@keyframes in_p%d{0%%{opacity:0}%s%%{opacity:0}%s%%{opacity:1}100%%{opacity:1}}"
            % (n, pct(max(0.0, e["start"] - 0.12)), pct(e["start"]))
        )
svg = svg.replace("</style>", "".join(extra) + "</style>")

with open("whoami.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print(f"typing ends: {TYPE_END:.2f}s   loop: {TOTAL:.2f}s   size: {WIDTH}x{HEIGHT}")
print(f"bytes: {len(svg)}")
