# HANDOVER - 2026-06-13 15:51 UTC

> The UI/UX redesign plus follow-on fixes (Workstreams A–C, shipped as PRs
> against `yoyocatw/SquashVote`), then a new **clip replay-window feature**
> (Workstream D, 2026-06-13 15:51 UTC — uncommitted on `uiux-redesign`).
> Sections are timestamped; the header time is the most recent update.

## TL;DR

The `uiux-redesign` redesign is **complete, tested, and split into four clean,
independent, mergeable PRs**. Nothing is technically blocking — it's waiting on
the upstream maintainer (YoYo Chan) to review/merge. Two latent bugs found along
the way were fixed as their own small PRs.

| PR | Branch | What | State |
|----|--------|------|-------|
| [#2](https://github.com/yoyocatw/SquashVote/pull/2) | `redesign/docs` | Docs / design system (docs only) | OPEN · MERGEABLE |
| [#3](https://github.com/yoyocatw/SquashVote/pull/3) | `redesign/app` | The redesign + 42 tests + review fixes (3 commits) | OPEN · MERGEABLE |
| [#4](https://github.com/yoyocatw/SquashVote/pull/4) | `fix/comment-user-default` | `default="Anonymous"` FK bug + migration | OPEN · MERGEABLE |
| [#5](https://github.com/yoyocatw/SquashVote/pull/5) | `fix/moderation-auth` | Security: gate accept/reject video actions | OPEN · MERGEABLE |
| [#6](https://github.com/yoyocatw/SquashVote/pull/6) | `feature/clip-replay-window` | Clip replay window + optional end timestamp (Workstream D) | OPEN · stacked on #3 |
| ~~#1~~ | — | Old combined PR | CLOSED (superseded by #2/#3) |

`origin` = `github.com/yoyocatw/SquashVote` (upstream, the live site). `fork` =
`github.com/SpunkyMartian/SquashVote` (PR branches live here).

**New since last handover:** Workstream D — clips now play their window **once
then offer a Replay button** (was: play endlessly), with an **optional uploader
end timestamp**. Committed as `a1bed19` on branch `feature/clip-replay-window`
(off `uiux-redesign`); opened as **[PR #6](https://github.com/yoyocatw/SquashVote/pull/6)
against `origin/main`, stacked on #3** (its diff carries the whole redesign until
#3 merges, then auto-collapses to the ~12 feature files). 54 tests green (was 42).

---

## Workstream A — UI/UX redesign (2026-06-13 12:55 UTC)

### What got done
Full mobile-first dark redesign (designed in Paper, file "squash-vote"):
homepage hero, new `/browse/` page (filter tabs All/PSA/Amateur/Unvoted,
pagination, "X of Y voted"), clip/vote page (Plyr 20s clip, locked pre-vote
preview, post-vote reveal with **pure CSS bars — Chart.js removed**, "Next One"
CTA, "More decisions" suggestions), restyled secondary pages, minimal
header + Alpine slide-out menu + shared footer. `#0A0A0A` theme, Space Grotesk
headings.

Then a **multi-agent review** (6 lenses: UX/flow, SEO/GEO, chrome, code,
correctness, a11y) surfaced 35 findings; 34 were implemented and folded into
PR #3 (commit "apply multi-lens review fixes"). Highlights:
- **SEO/GEO**: per-page canonical (was homepage-only), overridable OG/Twitter +
  `og:image` per clip, `sitemap.xml`, `robots.txt`, JSON-LD (`WebSite` +
  per-clip `VideoObject`).
- **UX**: last-clip "Browse all" fallback, empty states, comment thread no
  longer resets on post (preserves likes/reports/sort + live count via OOB).
- **a11y**: global `:focus-visible` ring, `[x-cloak]` (no menu flash), vote
  radios in `fieldset`, aria-labels, AA contrast (`#FFFFFF80`+), Escape closes menu.
- **cleanup**: shared `_clip_row.html` + `footer.html` partials; deleted
  byte-identical `post_vote_inline.html` + unused `already_voted.html`; removed
  dead `chart` view/route; deduped view logic via `get_voted_video_ids()` /
  `vote_percentages()` helpers.

### Rebase + upstream integration (the hard part)
The branch had drifted ~1 commit behind upstream. Rebased `uiux-redesign` onto
`origin/main` (`d95a4e0`, which added a result-page recommendation feature + a
`/guide/` page). Re-integrated that feature into the new design rather than
clobbering it: kept the `suggested_videos` query (now the "More decisions"
section), restyled `guide.html` to the dark theme, linked it in the menu/footer.

### Why 4 PRs, not a 3-way stack of the redesign
The redesign's theme/chrome/screens/backend are **one atomic, deployable unit** —
`base.html` links to `/browse/`, whose view/template ship with the screens, so a
theme-only PR 500s on every page (`NoReverseMatch: 'browse'`). Upstream
**auto-deploys to the live site on every merge to `main`** (`.github/workflows/
fly-deploy.yml`), so a partial merge would deploy a broken site. **Only docs
separates cleanly.** Do not try to split the implementation further.

### Tests
`vote/tests.py` — 42 tests (models, forms, vote flow + dedup, browse filters/
pagination, get_next_decision/suggested_videos, comments, smoke, plus regression
tests for the review fixes). All green **under Python 3.13** (see gotchas).

---

## Workstream B — `default="Anonymous"` FK bug → PR #4 (2026-06-13)

`Comment.user` and `CommentReport.user` had `default="Anonymous"` — a string
where a `User` pk/None is expected. Any code creating a comment without an
explicit `user` crashes (`ValueError: Field 'id' expected a number but got
'Anonymous'`). The app dodged it because every view passes `user=` explicitly.
Discovered while writing the test suite. Removed the default + added migration
`0006_alter_comment_commentreport_user.py` (state-only). Surgical — deliberately
does **not** touch the pre-existing, unrelated `unique_video_id_timestamp`
constraint drift on `main` (commented out in the model but never migrated; left
as-is). Independent of the redesign (touches `models.py` only).

---

## Workstream C — moderation auth security fix → PR #5 (2026-06-13 12:55 UTC)

`accept_video` / `reject_video` (`/video/<id>/accept|reject/`) had **no access
control and accepted GET** — `GET /video/5/reject/` deletes decision #5
(drive-by / CSRF-able). Only the review *list* (`/review/`) was `@login_required`.
Added `@login_required` + `@require_POST` to both. `review.html` already calls
them via `hx-post` (CSRF token wired on `<body>`), so the admin UI is unaffected.
Test in `vote/test_moderation.py` (separate file to avoid clashing with PR #3's
`tests.py`), 4 tests, green on 3.13.

**Clarification on "login":** the **community side has no login at all** (voting/
commenting/liking/reporting are anonymous, session-based; no signup route). The
only login is **admin/moderation** for the site owner: `/superuser/` (Django
admin) and `/login/` → `/review/` (`@login_required`, superuser-only).

---

## Workstream D — clip replay window (2026-06-13 15:51 UTC)

**Problem.** A clip started at the uploader's timestamp and then played to the
**end of the whole YouTube video** ("plays endlessly"). The old `plyr.js` had no
stop/loop logic at all — and a latent bug: its `seeking` handler referenced an
**undefined `end`** (threw the instant anyone scrubbed) plus a dead `replayButton`
listener with no button. The CLAUDE.md "20s window, auto-loops" line was
aspirational; the code never did it.

**Decision (user).** Clip end = an **optional** uploader `end_timestamp`; blank ⇒
default 20s window. Behaviour = **play once, then a Replay button** (not auto-loop).

**What changed:**
- `vote/models.py`: new optional `Video.end_timestamp` field; `Video.end` property
  (uploader value if it parses and is after start, else `start +
  DEFAULT_CLIP_SECONDS`). New module constants `DEFAULT_CLIP_SECONDS=20`,
  `MIN_CLIP_SECONDS=2`, `MAX_CLIP_SECONDS=90`. `create_url()` updated to use them.
- `vote/migrations/0006_video_end_timestamp.py`: **adds the field only.** ⚠️ Django
  wanted to bundle a `RemoveConstraint(unique_video_id_timestamp)` (the
  pre-existing drift in "Next steps" #3) — I stripped it so the migration stays
  scoped. **Numbering caveat:** this is `0006` off `0005`; PR #4 also introduces a
  `0006_*` off `0005`. When both reach `main` there'll be two leaves →
  `makemigrations --merge` (or renumber one). Maintainer's merge-time concern.
- `vote/forms.py`: `end_timestamp` added to `VideoForm`; `clean()` validates it
  (parses, after start, 2–90s window) via a `parse_timestamp()` helper.
- `static/js/plyr.js`: rewritten — reads `data-start`/`data-end`, plays the window
  once, on `timeupdate >= end` pauses + rewinds to start + shows the Replay
  overlay, clamps scrubbing to `[start,end]`, restarts cleanly on Replay or the
  native play button. Undefined-`end` bug + dead code gone.
- `vote/templates/vote/video_result.html`: `data-end` on `#player`, wrapper made
  `relative`, hidden `#replayButton` overlay (circular replay icon + "Replay").
  View passes `end = video.end`.
- `vote/templates/vote/video_form.html`: Start/End-(optional) two-column grid +
  helper copy; **now renders form errors** (it silently swallowed them before) and
  preserves submitted values on validation failure.
- `vote/templates/vote/guide.html`: step 3 rewritten for start + optional end.
- `vote/tests.py`: +12 tests (end property, form validation, player wiring). 54 total.
- `static/css/output.css` rebuilt (new error-red `#F87171` + overlay utilities).
- `.claude/launch.json`: added so the preview tooling can run the dev server
  (`DEBUG=True … runserver $PORT`). Dev-only helper; remove if unwanted.

**Verified** (Claude Preview, real browser on clip #9, window 30–50):
player initialised, no console errors, snapped to start; drove playback past the
end → it paused, rewound to start, revealed Replay; Replay restarted from start;
upload form shows the End field and rejects `end < start` with the value
preserved. 54/54 tests green on Python 3.13.

**Status:** committed as `a1bed19`, pushed to `fork/feature/clip-replay-window`,
opened as **[PR #6](https://github.com/yoyocatw/SquashVote/pull/6)** against
`origin/main` (stacked on #3 — diff collapses to the feature once #3 merges).
**Open:** the existing ~20 seeded clips have no `end_timestamp` → all use the 20s
default until re-edited. `.claude/launch.json` (preview-server config) is left
**untracked/uncommitted** — gitignore or delete if unwanted.

---

## Lessons learned / gotchas (read before you touch anything)

1. **Run tests with Python 3.13, NOT the local `.venv` (3.14).** Django 5.1.5's
   test client crashes on Python 3.14 (`Context.__copy__` AttributeError in the
   test render instrumentation). The repo's `.venv` is 3.14; prod/Docker is 3.13.
   A throwaway 3.13 venv was used: `/tmp/sv313/bin/python manage.py test vote`
   (recreate with `python3.13 -m venv … && pip install Django==5.1.5
   django-environ google-api-python-client whitenoise` if it's gone).
   `manage.py check`, `makemigrations`, `migrate`, `runserver` all work fine on 3.14.
2. **`CanonicalUrlMiddleware` 301-redirects every host except `squashvote.wtf`.**
   On `main` it's unconditional → this is why upstream has no working tests and
   why local dev historically needed it commented out. The redesign makes it
   `if not DEBUG`. For tests off `main` (e.g. PR #5) use
   `Client(SERVER_NAME="squashvote.wtf")`.
3. **`output.css` is generated** — rebuild with
   `npx @tailwindcss/cli -i ./static/css/input.css -o ./static/css/output.css`
   after editing `input.css` or adding new utility classes. Never hand-edit it.
4. **Local dev no longer needs manual settings edits** — `DEBUG=True python
   manage.py runserver` is enough on the redesign branch (cookie security +
   `CanonicalUrlMiddleware` are now `DEBUG`-conditional; localhost is in
   `ALLOWED_HOSTS`). The CLAUDE.md "Quick start" steps about editing settings are
   now stale for this branch.
5. **The two fix PRs (#4, #5) are branched off `origin/main`, not on
   `uiux-redesign`.** So the local canonical branch / dev server does NOT carry
   them; they reach `main` via their own PRs. No conflicts between any of the 4 PRs
   (verified — they touch disjoint regions).
6. **`backup/uiux-pre-rebase` tag** holds the pre-rebase tip (`693ce30`) in case
   the rebase needs unwinding.

---

## Next steps (prioritized)

1. **Maintainer review/merge of #2, #3, #4, #5.** Nudge YoYo — the old #1 sat
   untouched since April. Merge order doesn't matter (all independent), though
   #4/#5 are tiny and safe to land first.
2. **(Optional) Restyle admin `vote/templates/vote/review.html`** — still old
   light-theme DaisyUI + an emoji. Low priority: login-gated, admin-only, not
   user-facing. Left as the one un-done review finding.
3. **(Maintainer decision) The `unique_video_id_timestamp` constraint drift** on
   `main` — model has it commented out but no migration removed it; PR #4 left it
   untouched. Decide: enforce it or formally drop it (its own migration).
4. **After PRs merge — cleanup:** delete stale `fork/Anvith-Reddy-N/uiux-redesign`
   (old #1 branch, pre-rebase), the merged `redesign/*` + `fix/*` fork branches,
   local `claude/stoic-elion-db3da9` worktree branch, and `git tag -d
   backup/uiux-pre-rebase`.

---

## File map (most important first)

### New this session
| File | What it is |
|------|-----------|
| `vote/sitemaps.py` | `VideoSitemap` + `StaticViewSitemap` (SEO) |
| `vote/templates/vote/partials/_clip_row.html` | Shared compact clip row (browse + suggestions) |
| `vote/templates/vote/partials/footer.html` | Shared site footer (included by `base.html` on every page) |
| `vote/tests.py` | 42-test suite for the vote app (run on 3.13) |
| `vote/test_moderation.py` | 4 moderation access-control tests (PR #5) |
| `vote/migrations/0006_alter_comment_commentreport_user.py` | PR #4 only — drops the bad FK default |

### Core code
| File | Role |
|------|------|
| `vote/views.py` | All views (function-based). Helpers: `get_voted_video_ids`, `vote_percentages`, `get_next_decision`. `accept/reject_video` now gated (PR #5 branch). |
| `vote/urls.py` | Routes incl. new `sitemap.xml` + `robots.txt`; `chart` route removed |
| `vote/models.py` | `Video.get_absolute_url()` + `.slug` (fixes slug-500; powers sitemap). PR #4 removes the `Anonymous` FK default. |
| `squashvote/settings.py` | `django.contrib.sitemaps` added; cookie/middleware `DEBUG`-conditional |
| `static/css/input.css` | Theme tokens, `:focus-visible`, `[x-cloak]` (regenerate `output.css`) |

### Templates
`base.html` (header/menu/footer + SEO `<head>` blocks), `index.html`,
`browse.html` + `partials/browse_list.html`, `video_result.html` +
`partials/post_vote.html` + `partials/comment_section.html` + `partials/replies.html`,
`guide.html`, `video_form.html`, `about.html`. `review.html` = admin, still old style.

### Docs
`CLAUDE.md` (project guide — being updated alongside this handover),
`docs/PRODUCT.md`, `docs/BRAND.md`, `docs/DESIGN_SYSTEM.md`.

---

## Dev environment

- **Branch**: `uiux-redesign` in `~/My Code/SquashVote` (canonical local; = redesign + review fixes, minus the #4/#5 fixes which are off `main`)
- **Run**: `source .venv/bin/activate && DEBUG=True python manage.py runserver` (3.14 venv is fine for running)
- **Test**: `/tmp/sv313/bin/python manage.py test vote` (3.13 only)
- **CSS**: `npm run dev` (watch) or the one-shot `npx @tailwindcss/cli …` above
- **DB**: SQLite `db.sqlite3`, ~20 seeded videos (gitignored; prod = Postgres on Fly.io)
- **A dev server may still be running on `:8000`** from this session.
