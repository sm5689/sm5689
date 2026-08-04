# Setup

Everything is already filled in for `sm5689`. Four things to do, in order.

## 1. Run the snake action FIRST

The snake image at the bottom of the README points at a branch that does not
exist yet, so it will render broken until the action runs once.

1. Commit `.github/workflows/snake.yml`
2. Go to the repo's **Actions** tab
3. Select **Generate contribution snake** and click **Run workflow**

It creates an `output` branch containing `snake.svg`. After that it self-updates
every 12 hours.

## 2. Confirm the animated terminal renders

`assets/whoami.svg` must live at that exact path relative to the README.
GitHub serves it through its image proxy, and the CSS keyframes inside animate
normally in that context. If you ever move the file, update the `src`.

If the animation does not play but the text shows correctly, the CSS was
stripped — the SVG is built to degrade gracefully, so you get a readable static
terminal rather than a blank box.

To edit the content, change the `LINES` list in `gen_whoami.py` and re-run it.
Timings, clip widths, and canvas height all recompute automatically.

## 3. Fix the pinned repos

This is the highest-value change on this list.

Your four most-starred repos are forks: `F.L.A.P`, `Py-progs`,
`FlutterSchoolAppUI`, `NewsAppApi`. Pinned forks read as padding to anyone
technical, and GitHub labels them "Forked from" right on the card.

Go to your profile, click **Customize your pins**, and pin original work only:

- Threadwire
- Roommate Peacekeeper
- portfolio
- cppCodes
- plus two more originals

If Threadwire and Roommate Peacekeeper are private, make them public or the
Featured Work table links nowhere. They are the two projects you actually
position in applications, so they should be the two things a recruiter can
click.

## 4. Add repo names to the pin cards

The Featured Work section has live cards for `portfolio` and `cppCodes` only,
because those are the repo slugs I could verify. Once Threadwire and Roommate
Peacekeeper are public, add cards using their exact slugs:

```
https://github-readme-stats.vercel.app/api/pin/?username=sm5689&repo=EXACT_SLUG&theme=github_dark&hide_border=true&border_radius=8
```

The slug is case-sensitive and must match the URL exactly. A wrong slug is a
broken image, which is what produced the empty boxes in your first preview.

---

## Why the first version broke

Four separate causes, all fixed:

| Symptom | Cause |
|---|---|
| Stray `-->` as visible text | Nested HTML comments. `<!--` cannot contain another `<!--`; the outer comment closed early at the first `-->` and the remainder rendered as text. This version has zero HTML comments. |
| Broken image boxes | `YOUR_USERNAME` / `REPO_ONE` placeholders were never substituted, so the card services returned errors. |
| "Can't fetch any contribution" | Same placeholder issue on the streak service. |
| "User Not Found" on LeetCode card | Handle was `YOUR_HANDLE` instead of `surajmishragemini`. |
| "1 contribution since Jun 3 2011" | The streak service's fallback response for a nonexistent user. |

## Known limitations

- `count_private=true` was removed from the stats card. Public instances of
  github-readme-stats cannot see private repos, so it silently did nothing.
  Self-host with a personal access token if you want private commits counted.
- The public Vercel instances get rate-limited at peak hours and cards
  intermittently fail. Self-hosting github-readme-stats is free and takes about
  five minutes if that annoys you.
- Keep one theme across every card. Mismatched themes are the single most
  common thing that makes a profile look unfinished.
