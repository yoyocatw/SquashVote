# HANDOVER - 2026-04-13

## Summary

Full UI/UX redesign of SquashVote (squashvote.wtf) — three core screens redesigned in Paper (paper.design), then implemented as Django templates with HTMX. All code changes are **uncommitted** on the `uiux-redesign` branch in the git worktree at `/Users/anvith/.superset/worktrees/SquashVote/uiux-redesign`.

**Status: Code written, NOT yet tested on localhost. NOT committed.**

---

## What was done

### 1. Paper design finalization
- Arranged three finalized screens in Paper: Homepage (Hero), Library/Browse (Elias vs Asal BG), Clip (Vote/Results)
- Iterated on background image positioning for Library/Browse — used oversized rectangle + left/top offset technique (same as Post-Vote screen) for precise image cropping
- Named them `FINAL — 1. Homepage`, `FINAL — 2. Library / Browse`, `FINAL — 3. Clip (Vote/Results)`

### 2. Foundation — CSS + Base template
- **`static/css/input.css`**: Replaced Montserrat/Chewy with Space Grotesk. Updated `customblack` theme to `#0A0A0A` base. Added `--color-vote-stroke/let/nolet` CSS vars. Added `--font-heading` token.
- **`vote/templates/vote/base.html`**: Complete rewrite. Replaced full DaisyUI navbar with minimal header (back arrow / "SquashVote.wtf" / hamburger). Alpine.js slide-out menu. Removed Chart.js CDN, confetti.js, easter.js, april_fools.js, modal.js, theme-change.js. Added `htmx:afterSwap` Alpine re-init listener.

### 3. Browse page (NEW)
- **`vote/views.py`** — New `browse()` view: filters (All/PSA/Amateur/Unvoted), pagination (15/page), "X of Y voted" counter, NEW/Voted badge logic
- **`vote/urls.py`** — Added `path("browse/", browse, name="browse")`
- **`vote/templates/vote/browse.html`** — Full-bleed background (YouTube thumbnail fallback), sticky filter tabs, HTMX-powered filtering
- **`vote/templates/vote/partials/browse_list.html`** — Compact row layout with thumbnails, badges, chevrons

### 4. Homepage redesign
- **`vote/views.py`** — Simplified `index()`: fetches "new this week" (7-day window, fallback to latest 8), passes `section_title`, `total_decisions`
- **`vote/templates/vote/index.html`** — Hero section with full-bleed background + gradient overlay, "The crowd's verdict on controversial calls." headline, "Start Voting →" CTA, horizontal scrolling clip cards, minimal footer

### 5. Clip page redesign
- **`vote/templates/vote/video_result.html`** — Full-bleed blurred YouTube thumbnail background, Plyr player, redesigned vote form (no emoji, clean radio buttons), `hx-target="#post-vote-area"`
- **`vote/views.py`** — Added `get_next_decision()` helper (newest unvoted). Added `stroke_pct/let_pct/nolet_pct/vote_display/next_video` to context. Updated POST handler to return `post_vote.html` with full post-vote content.
- **`vote/templates/vote/partials/post_vote.html`** — HTMX response: verdict cards + CSS bar chart + comments + "Next Decision →" CTA
- **`vote/templates/vote/partials/post_vote_inline.html`** — Same layout for full page reload (when already voted)
- **`vote/templates/vote/partials/already_voted.html`** — Simplified to verdict cards only (legacy compat)

### 6. Documentation
- **`CLAUDE.md`** — Updated with redesign screens, implementation decisions, contribution workflow, "DO NOT" list
- **`docs/DESIGN_SYSTEM.md`** — Locked in Space Grotesk, vote colors, CSS bars, full-bleed BG pattern

---

## What worked

- Paper MCP for design iteration — especially the oversized-rectangle positioning technique for background images
- Tailwind CSS v4 + DaisyUI theme system — custom properties integrate cleanly
- The HTMX post-vote flow design: single `hx-target="#post-vote-area"` that replaces vote form with verdict + bars + comments + next CTA in one response

## What didn't work / gotchas

- **Worktree location**: Changes are in `/Users/anvith/.superset/worktrees/SquashVote/uiux-redesign`, NOT in `~/My Code/SquashVote`. The IDE sidebar shows the main repo. Need to either:
  - Open the worktree directory in the IDE, OR
  - Checkout `uiux-redesign` branch directly in `~/My Code/SquashVote` and copy changes there
- **No virtualenv found** in the worktree — `python3` is system Python without Django installed. Need to set up venv or use existing one to test locally.
- **Browse page background image**: Currently uses a YouTube thumbnail URL (`AYlKicTjq7A`) as placeholder. Should be replaced with a proper static image for reliability. Same for homepage hero.
- **CSS compilation**: Works fine with `npx @tailwindcss/cli -i ./static/css/input.css -o ./static/css/output.css`. Must run `npm install` first in the worktree.
- **`video.create_url`** in the clip template — relies on the model method. Should still work but wasn't tested.
- **Comment section partial** (`comment_section.html`) was NOT restyled — it still uses old DaisyUI classes. Will look inconsistent.

---

## Key decisions

| Decision | Why |
|----------|-----|
| Drop Chart.js → CSS bars | Design system says no Chart.js. Eliminates 44KB CDN, `/chart/` API, MutationObserver theme watcher. Simpler. |
| Space Grotesk for headings | Design system recommended it over Montserrat — tighter, more utilitarian. |
| Minimal header (no full navbar) | Paper designs show back arrow / logo / hamburger. Matches the focused, single-purpose feel. |
| `browse()` as separate view | Homepage becomes a landing page; browse absorbs all the filter/pagination logic. Clean separation. |
| Session-based "Unvoted" filter | `VoteUser.filter(session_id=...).values_list("video_id")` then `.exclude()`. Efficient at current scale. |
| `get_next_decision()` = newest unvoted | Simple first. Can enhance later with vote-split scoring. |
| `post_vote.html` returns everything | Single HTMX response with verdict + bars + comments + next CTA. Avoids complex OOB swaps. |

---

## Next steps (prioritized)

### Must do before testing
1. **Set up Python virtualenv** in the working directory and install requirements
2. **Run `npm install && npm run dev`** to compile CSS in watch mode
3. **Run `python manage.py runserver`** and test all three pages
4. **Local dev settings**: Add `127.0.0.1`/`localhost` to ALLOWED_HOSTS, set `SESSION_COOKIE_SECURE=False`, `CSRF_COOKIE_SECURE=False`, comment out `CanonicalUrlMiddleware`

### Must fix before PR
5. **Restyle `comment_section.html`** — still uses old DaisyUI classes (voting buttons, color classes). Needs to match the dark, minimal aesthetic.
6. **Add static hero images** — download/optimize the El Sherbini and Elias vs Asal photos to `static/images/hero-home.jpg` and `static/images/hero-browse.jpg`. Currently using YouTube thumbnail URLs as placeholders.
7. **Test the HTMX vote flow end-to-end** — submit vote → verify post_vote.html renders correctly → verify comments load → verify "Next Decision" links work
8. **Test browse page filters** — All/PSA/Amateur/Unvoted tabs, pagination
9. **Test other pages** (about, rules, video_form, confirm) still render with new base template
10. **Remove `print()` debug statement** in views.py (was in old code, removed in rewrite — verify)

### Nice to have
11. Replace YouTube thumbnail placeholder in browse.html with static image
12. Add `show_back=True` to about/rules/video_form views for back navigation
13. Responsive testing at 390px, 768px, 1440px

### Commit & PR
14. Commit all changes on `uiux-redesign` branch
15. Push to `fork` remote (`SpunkyMartian/SquashVote`)
16. Create PR against `origin/main` (`yoyocatw/SquashVote`)

---

## File map

### Modified files
| File | What it does |
|------|-------------|
| `CLAUDE.md` | Project guide — updated with redesign context |
| `docs/DESIGN_SYSTEM.md` | Visual spec — locked in final decisions |
| `static/css/input.css` | Tailwind source — Space Grotesk, #0A0A0A theme, vote color vars |
| `static/css/output.css` | Compiled CSS (auto-generated, don't edit) |
| `vote/views.py` | All views — new `browse()`, `get_next_decision()`, modified `index()` and `video_result()` |
| `vote/urls.py` | Routes — added `/browse/` |
| `vote/templates/vote/base.html` | Base layout — minimal header, slide-out menu, cleaned scripts |
| `vote/templates/vote/index.html` | Homepage — hero landing + "New this week" cards |
| `vote/templates/vote/video_result.html` | Clip page — full-bleed BG, vote form, post-vote area |
| `vote/templates/vote/partials/already_voted.html` | Simplified verdict cards |

### New files
| File | What it does |
|------|-------------|
| `vote/templates/vote/browse.html` | Library/Browse page — full-bleed BG, filter tabs, list container |
| `vote/templates/vote/partials/browse_list.html` | Browse list rows — HTMX partial for filtering/pagination |
| `vote/templates/vote/partials/post_vote.html` | HTMX response after vote — verdict + bars + comments + next CTA |
| `vote/templates/vote/partials/post_vote_inline.html` | Same as above but for full page reload (already voted) |

### Untouched but relevant
| File | Why it matters |
|------|---------------|
| `vote/templates/vote/partials/comment_section.html` | NOT restyled — will look inconsistent. Priority fix. |
| `vote/templates/vote/about.html` | Uses `bg-base-300` — should still work but needs visual check |
| `vote/templates/vote/video_form.html` | Upload form — needs visual check with new base template |
| `vote/models.py` | No changes needed — all models untouched |
| `static/js/plyr.js` | Still loaded — video player still works |
| `static/js/chart.js` | No longer loaded in base.html — can be deleted after verification |

---

## Contribution context

- **Upstream repo**: `https://github.com/yoyocatw/SquashVote` (remote: `origin`)
- **Fork**: `https://github.com/SpunkyMartian/SquashVote` (remote: `fork`)
- **Branch**: `uiux-redesign`
- **CI/CD**: Push to `main` on origin auto-deploys to Fly.io
- **Worktree path**: `/Users/anvith/.superset/worktrees/SquashVote/uiux-redesign`
- **Main repo path**: `/Users/anvith/My Code/SquashVote` (on `main` branch)
