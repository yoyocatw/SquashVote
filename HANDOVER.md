# HANDOVER - 2026-04-14

## Summary

Full UI/UX redesign of SquashVote (squashvote.wtf). Three core screens + hamburger menu + footer designed in Paper (paper.design), then implemented as Django templates. Code is on the `uiux-redesign` branch in `~/My Code/SquashVote` (worktree was removed, branch checked out directly). Previous commit exists (`c9755a4`), current changes are **uncommitted on top of that**.

**Status: Implemented, tested on localhost (port 8080), copy/brand audit done, NOT committed, NOT pushed.**

---

## What got done

### Paper design (paper.design file: "squash-vote")
- **5 FINAL screens** organized in top row: Homepage → Browse → Clip → Hamburger Menu → Footer
- **11 archived iterations** moved to bottom rows, renamed with "ARCHIVE —" prefix
- Copy audit done and applied: "Make Your Call →", "YOUR CALL" / "THE REF SAID", "make your call to view results & comments"
- Locked preview designed for pre-vote state: frosted panel with ghost verdict cards, ghost bar chart, ghost comment lines, 32px lock icon

### Code implementation
1. **CSS foundation** (`static/css/input.css`): Space Grotesk added, theme updated to #0A0A0A, vote color vars, `font-heading`/`font-body`/`font-bebas` tokens
2. **Base template** (`vote/templates/vote/base.html`): Minimal header (back/logo/hamburger), Alpine.js slide-out menu, removed Chart.js/confetti/easter/modal scripts
3. **Browse page** (NEW): `vote/views.py` → `browse()` view, `vote/urls.py` → `/browse/`, filter tabs (All/PSA/Amateur/Unvoted), pagination, "X of Y" counter, NEW/Voted badges
4. **Homepage**: Hero landing with background image, "Make Your Call →" CTA, "New this week" horizontal cards, footer
5. **Clip page**: Full-bleed background, Plyr video embed, vote buttons, locked preview panel, post-vote HTMX flow with CSS bars (replaced Chart.js)
6. **Real production data seeded**: 20 videos scraped from squashvote.wtf with real vote breakdowns via `/chart/` API

### What was fixed during session
- **Worktree → direct checkout**: Moved from `.superset/worktrees/` to `~/My Code/SquashVote` on `uiux-redesign` branch
- **Font loading**: Replaced brittle `font-['Space_Grotesk',system-ui,sans-serif]` with reliable `font-heading` token across all templates
- **Background images not showing**: Changed `fixed inset-0 -z-10` to `absolute inset-0` with explicit `z-index: 0/1` — fixed stacking context issue
- **Copy aligned to brand voice**: "Start Voting" → "Make Your Call", "YOU VOTED" → "YOUR CALL", "REF SAID" → "THE REF SAID", "unlock" → "view"
- **Local dev settings**: Added localhost to ALLOWED_HOSTS, made cookie security conditional on DEBUG, disabled CanonicalUrlMiddleware

---

## What didn't work / known issues

1. **Background images on browse + clip pages**: Fixed with z-index approach but should be verified — the `absolute` positioning means the background doesn't scroll with content on long pages. May need `fixed` with a different stacking approach for desktop.
2. **Comment section (`comment_section.html`) NOT restyled**: Still uses old DaisyUI classes. Will look inconsistent with the new dark minimal design.
3. **`settings.py` was modified for local dev**: ALLOWED_HOSTS, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE, CanonicalUrlMiddleware changes need to be reverted or made properly conditional before PR.
4. **No desktop/responsive testing done**: All designs are 390px mobile. No desktop breakpoints designed or tested. The content has `max-w-[640px]` in some places but not consistently.
5. **Static hero images are large**: hero-home.jpeg (247KB), hero-clip.jpeg (181KB), hero-browse.jpeg (112KB). Should be optimized/compressed before production.
6. **`db.sqlite3` has test data**: 20 real videos seeded locally but the DB file is gitignored. Production uses Postgres on Fly.io.
7. **Old JS files still in repo**: `static/js/chart.js`, `static/js/confetti.js`, `static/js/easter.js`, `static/js/april_fools.js`, `static/js/modal.js` — no longer loaded but not deleted.

---

## Key decisions

| Decision | Why |
|----------|-----|
| Drop Chart.js → CSS bars | Design system mandates it. Simpler, no CDN, percentages computed server-side |
| Space Grotesk for headings | Tighter, more utilitarian than Montserrat. Locked in design system. |
| `font-heading`/`font-body` tokens | Arbitrary Tailwind font classes were unreliable. Theme tokens work consistently. |
| "call" not "vote" in UI copy | Brand guide: "Call" for user's judgment, "vote" only for data counts |
| "view" not "unlock" | Per user feedback — "unlock" sounds gamified, which contradicts brand |
| Locked preview panel | Ghost content + lock icon hints at what's behind the vote without revealing data |
| `absolute` not `fixed` for backgrounds | `fixed -z-10` broke in some stacking contexts. `absolute` with explicit z-index works. |
| Real production data for testing | Scraped 20 videos + vote breakdowns from squashvote.wtf via chart API |

---

## Next steps (prioritized)

### Before committing
1. **Restyle `comment_section.html`** — match dark minimal aesthetic (Inter font, #FFFFFF opacity colors, no DaisyUI component classes)
2. **Verify background images work on all 3 pages** — hard refresh, check mobile and desktop
3. **Test the full vote → results → comments → Next Decision flow** end-to-end
4. **Test browse filter tabs** (All/PSA/Amateur/Unvoted) and pagination via HTMX
5. **Revert settings.py dev changes** or make them properly conditional (`if DEBUG:`)

### Before PR
6. **Delete old JS files**: chart.js, confetti.js, easter.js, april_fools.js, modal.js
7. **Optimize hero images** — compress to <100KB each
8. **Responsive testing** at 390px, 768px, 1440px
9. **Test other pages** (about, rules, video_form, confirm) still work with new base template
10. **Update HANDOVER.md** with final state

### PR workflow
11. Commit all changes on `uiux-redesign` branch
12. Push to `fork` remote (`SpunkyMartian/SquashVote`)
13. Create PR against `origin/main` (`yoyocatw/SquashVote`)
14. CI auto-deploys to Fly.io on merge

---

## File map

### Modified (uncommitted on top of c9755a4)
| File | What changed |
|------|-------------|
| `vote/views.py` | `browse()` view, `get_next_decision()`, simplified `index()`, percentage context in `video_result()` |
| `vote/templates/vote/base.html` | Minimal header, slide-out menu, cleaned scripts |
| `vote/templates/vote/index.html` | Hero landing, "Make Your Call", clip cards, footer |
| `vote/templates/vote/browse.html` | Full-bleed BG, filter tabs, list container |
| `vote/templates/vote/video_result.html` | Full-bleed BG, vote form, locked preview, post-vote area |
| `vote/templates/vote/partials/browse_list.html` | List rows with badges, thumbnails, chevrons |
| `vote/templates/vote/partials/post_vote.html` | HTMX response: verdict + bars + comments + Next CTA |
| `vote/templates/vote/partials/post_vote_inline.html` | Same for full page reload |
| `vote/templates/vote/partials/already_voted.html` | Simplified verdict cards |
| `squashvote/settings.py` | Local dev: ALLOWED_HOSTS, cookie security, middleware |
| `static/css/output.css` | Recompiled Tailwind |

### New files (untracked)
| File | What it is |
|------|-----------|
| `static/images/hero-home.jpeg` | Aboelkheir solo — homepage background (247KB) |
| `static/images/hero-browse.jpeg` | Elias vs Asal — browse background (112KB) |
| `static/images/hero-clip.jpeg` | Coll vs Farag — clip background (181KB) |
| `static/images/aboelkheir.jpeg` | Original download (duplicate of hero-home) |
| `static/images/coll-v-farag.jpeg` | Original download (duplicate of hero-clip) |

### Already committed (in c9755a4)
| File | What it has |
|------|------------|
| `CLAUDE.md` | Full project guide with redesign context |
| `docs/DESIGN_SYSTEM.md` | Locked-in design system: fonts, colors, bars, BG pattern |
| `docs/BRAND.md` | Voice, tone, terminology |
| `docs/PRODUCT.md` | Product identity |
| `static/css/input.css` | Tailwind source: Space Grotesk, #0A0A0A theme, vote color vars |
| `vote/urls.py` | Added `/browse/` route |

### Untouched but needs attention
| File | Why |
|------|-----|
| `vote/templates/vote/partials/comment_section.html` | NOT restyled — old DaisyUI classes |
| `vote/templates/vote/about.html` | Needs visual check with new base template |
| `vote/templates/vote/video_form.html` | Needs visual check with new base template |
| `static/js/chart.js` | No longer loaded — safe to delete |
| `static/js/confetti.js` | No longer loaded — safe to delete |

---

## Dev environment

- **Branch**: `uiux-redesign` in `~/My Code/SquashVote`
- **Virtualenv**: `.venv/` (Python 3.14, Django 5.1.5)
- **Dev server**: `source .venv/bin/activate && python3 manage.py runserver 8080`
- **CSS watcher**: `npm run dev`
- **Database**: SQLite (`db.sqlite3`) with 20 real videos seeded
- **Upstream**: `origin` → `github.com/yoyocatw/SquashVote`
- **Fork**: `fork` → `github.com/SpunkyMartian/SquashVote`

## Paper design file
- File: "squash-vote" on paper.design
- Top row (L→R): FINAL 1. Homepage, FINAL 2. Browse, FINAL 3. Clip, Hamburger Menu, Footer
- All archived iterations in rows below
