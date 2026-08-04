# Setup

Every image that broke was a third-party service. The fix is to stop using them.

**Before:** 6 images from 4 external hosts, any of which could go down.
**Now:** 4 images generated as committed files in your own repo. Only shields.io
badges and the view counter are external, and shields.io is the most reliable
badge host on the internet.

| Image | Source | Status |
|---|---|---|
| `whoami.svg` | `gen_whoami.py` | committed file |
| `leetcode.svg` | `gen_leetcode.py` via Actions | committed file |
| `metrics.svg` | lowlighter/metrics via Actions | committed file |
| `snake.svg` | Platane/snk via Actions | committed file |

Deleted: `github-readme-stats.vercel.app`, `streak-stats.demolab.com`,
`github-readme-activity-graph.vercel.app`, `leetcard.jacoblin.cool`.

---

## Target layout

```
sm5689/
├── .github/
│   └── workflows/
│       ├── leetcode.yml
│       ├── metrics.yml
│       └── snake.yml
├── README.md
├── gen_whoami.py
├── gen_leetcode.py
├── whoami.svg          committed now
├── leetcode.svg        created by Actions
├── metrics.svg         created by Actions
└── snake.svg           created by Actions
```

**Creating folders in the GitHub web UI:** Add file > Create new file, then type
the full path into the filename box:

```
.github/workflows/leetcode.yml
```

Typing `/` creates the folder. There is no folder button. Delete any old
root-level `snake.yml`.

---

## Steps

### 1. Commit the files
All three workflows into `.github/workflows/`. `README.md`, `gen_whoami.py`,
`gen_leetcode.py`, `whoami.svg` at the root.

### 2. Add the METRICS_TOKEN secret
Only `metrics.yml` needs it. The other two work with the default `GITHUB_TOKEN`.

1. **Settings > Developer settings > Personal access tokens > Tokens (classic)**
2. Generate, scopes `repo` + `read:user`, no expiration
3. `sm5689` repo > **Settings > Secrets and variables > Actions > New repository secret**
4. Name it exactly `METRICS_TOKEN`

### 3. Run all three workflows manually
**Actions** tab, select each, **Run workflow**. Until they run, three of the four
images do not exist. That is expected, not a bug.

### 4. Check the run logs if anything is still blank
A blank image after a successful run means the file was not committed. A failed
run tells you why in the log.

---

## If the LeetCode workflow fails

LeetCode sometimes returns `403 Forbidden` to datacenter IPs, and GitHub Actions
runners are datacenter IPs. I could not test the live request from my
environment, so treat this as the known risk.

`gen_leetcode.py` is written to fail safely: on a bad response it exits non-zero
without writing, so a previously good `leetcode.svg` is never overwritten with a
broken one.

If the log shows a 403 or a timeout, fall back to the hosted card. Replace the
LeetCode line in README.md with this exact URL:

```
<img src="https://leetcard.jacoblin.cool/surajmishragemini?theme=dark&border=0&radius=8" alt="LeetCode" width="52%" />
```

Note there is no `font=` parameter. That is what broke it — I had set
`font=source_code_pro`, which is not a value that service accepts, so it errored
out. The card worked in your first preview and my edit broke it. The URL above
is the minimal form that works.

You can also verify the script locally before trusting the Action:

```bash
python3 gen_leetcode.py --mock      # offline, fake data, proves the renderer
python3 gen_leetcode.py             # live fetch
```

---

## The editor Preview tab lies

Relative paths like `./whoami.svg` never resolve in the **Preview** pane, because
nothing is committed yet and there is no file to point at. Some external images
also fail there.

Judge the result on your live profile page only.

---

## Editing

**Terminal text:** change the `LINES` list in `gen_whoami.py`, run
`python3 gen_whoami.py`, commit the new `whoami.svg`. Timings, clip widths and
canvas height recompute automatically.

**LeetCode card colors:** the palette constants at the top of `gen_leetcode.py`
match `whoami.svg` exactly. Change both together or they will drift.

---

## Still outstanding

Not a rendering problem, but the biggest remaining weakness:

1. **Your top repos are forks.** `F.L.A.P`, `Py-progs`, `FlutterSchoolAppUI`,
   `NewsAppApi` all carry a "Forked from" label. Profile > Customize your pins >
   originals only.

2. **Threadwire and Roommate Peacekeeper are not public.** The README describes
   both in detail and a reader cannot click either one. These are the two
   projects you lead with in applications. A polished README pointing at
   invisible work is worse than a plain README pointing at real work.
