# CLAUDE.md — SquashVote

## What is this?

SquashVote (squashvote.wtf) is a community voting platform for controversial squash referee decisions. Users watch YouTube clips of disputed calls and vote Stroke/Let/No Let, then see community results and discuss. Read `docs/PRODUCT.md` for the full product identity.

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Set up environment
cp .env.example .env
# Edit .env with your values (DATABASE_URL, SECRET_KEY, Google API keys); set DEBUG=True

# Run database migrations
python manage.py migrate

# Start CSS watcher (terminal 1)
npm run dev

# Start Django dev server (terminal 2) — DEBUG=True is all you need now
DEBUG=True python manage.py runserver
```

> With `DEBUG=True`, local dev needs **no manual settings edits** — cookie
> security and `CanonicalUrlMiddleware` are `DEBUG`-conditional, and
> `127.0.0.1`/`localhost` are in `ALLOWED_HOSTS`. (This was not always true; older
> notes about editing `settings.py` for local dev are obsolete.)

## Tech stack

- **Backend:** Django 5.1.5, Python 3.13
- **Frontend:** HTMX 2.0.4, Alpine.js 3.14.8, Tailwind CSS 4.1.11, DaisyUI 5.0.0-beta.2
- **Video:** Plyr 3.8.3 wrapping YouTube embeds — clip window plays once then offers Replay (default 20s, optional uploader-set end)
- **Vote results:** Pure CSS/HTML horizontal bars (Chart.js removed in redesign)
- **Database:** PostgreSQL (prod), SQLite (dev)
- **Deployment:** Fly.io (Docker, gunicorn, SJC region)
- **Static files:** WhiteNoise
- **Analytics:** Plausible
- **Fonts:** Space Grotesk (headings), Inter (body), Bebas Neue (logo)

## Project structure

```
squashvote/          # Django project settings (settings.py, urls.py, wsgi.py)
vote/                # Main app — all application code lives here
  models.py          # Video (+ get_absolute_url/slug), Result, VoteUser, Comment, CommentLike, CommentReport
  views.py           # All views (function-based, never CBV); helpers: get_voted_video_ids, vote_percentages, get_next_decision
  forms.py           # VideoForm, VoteForm, CommentForm
  urls.py            # App routes (+ sitemap.xml, robots.txt)
  sitemaps.py        # VideoSitemap + StaticViewSitemap (SEO)
  signals.py         # post_save: auto-create Result when Video created
  middleware.py      # CanonicalUrlMiddleware (domain redirect; DEBUG-conditional)
  admin.py           # Custom admin with reported comment actions
  tests.py           # Vote-app test suite (run under Python 3.13 — see Key commands)
  test_moderation.py # Access-control tests for accept/reject video
  templatetags/      # timestamp.py — comment_time filter (relative dates)
  utils/             # youtube_title.py — fetch title via Google API
  templates/vote/    # Full page templates
  templates/vote/partials/  # HTMX partials + shared _clip_row.html, footer.html
static/
  css/input.css      # Tailwind source (themes, fonts, :focus-visible, x-cloak)
  css/output.css     # Compiled CSS — generated; rebuild, never hand-edit
  js/                # plyr.js (the rest were removed in the redesign)
docs/                # Product, brand, and design system documentation
```

## Key commands

| Task | Command |
|------|---------|
| Dev server | `python manage.py runserver` |
| CSS watch | `npm run dev` |
| Migrations | `python manage.py migrate` |
| New migration | `python manage.py makemigrations vote` |
| Create admin | `python manage.py createsuperuser` |
| Collect static | `python manage.py collectstatic --noinput` |
| Tests | `python manage.py test` — **must run under Python 3.13** (Django 5.1.5's test client crashes on the repo's 3.14 `.venv`; prod/Docker is 3.13) |
| Rebuild CSS (one-shot) | `npx @tailwindcss/cli -i ./static/css/input.css -o ./static/css/output.css` |
| Deploy | Push to `main` (auto-deploys via GitHub Actions) or `flyctl deploy --remote-only` |

## Architecture patterns

### Views are always function-based
Every view is a plain function. No class-based views. Keep it that way.

### HTMX is the interaction layer
- Full page loads return templates extending `base.html`
- HTMX requests return partials from `templates/vote/partials/`
- Detect HTMX requests with: `request.headers.get("HX-Request")`
- CSRF token is set globally on `<body>` via `hx-headers`
- Common swap patterns: `hx-swap="innerHTML"` (replace children), `hx-swap="outerHTML"` (replace self)
- Out-of-band swaps used for cross-DOM updates: `hx-swap-oob="delete:#target"`

### Alpine.js handles local UI state
- Vote form radio selection: `x-data="{ vote: '' }"` with `x-model`
- Comment collapse/expand: `x-data="{ collapsed: false, reply: false, showReplies: false }"`
- After HTMX swaps, re-initialize Alpine: `Alpine.initTree(e.detail.target)` in `htmx:afterSwap`

### Session-based anonymous identity
- No login required for voting or commenting
- `get_session_id(request)` creates/retrieves session key
- Session cookie lasts 10 years
- Duplicate votes prevented by `UniqueConstraint(fields=["video", "session_id"])`
- Same pattern for comments, likes, reports

### Template organization
- `base.html` — navbar, CDN scripts, theme toggle, CSRF setup
- Page templates extend base and fill `{% block content %}` and `{% block scripts %}`
- Partials never extend base — they're HTML fragments for HTMX

### Theme system
- Two DaisyUI themes: `customblack` (dark, default) and `customlight`
- Defined in `static/css/input.css`
- Persisted via `localStorage.getItem('theme')`
- Vote results are server-computed CSS bars (Chart.js was removed in the redesign)

### Plyr video player
- Clips play the window `[Video.start, Video.end]` **once**, then pause, rewind to
  start, and reveal a **Replay** overlay button (no auto-loop). Logic lives in
  `static/js/plyr.js`, driven by `data-start` / `data-end` on `#player`.
- `Video.end` = the uploader's optional `end_timestamp` when it parses and falls
  after start, else `start + DEFAULT_CLIP_SECONDS` (20s). The `end_timestamp`
  upload field is optional; `VideoForm` validates it (after start, 2–90s window).
- Scrubbing is clamped to `[start, end]`; starts muted (autoplay policy), unmutes
  on first click.

## Data model

```
Video (the clip/decision)
├── video_id (YouTube ID)
├── video_title (fetched from YouTube API)
├── timestamp → converted to start seconds (Video.start)
├── end_timestamp → optional clip end; blank ⇒ start + 20s (Video.end property)
├── org_decision (Stroke | Let | No Let)
├── category (PSA | Amateur)
├── is_active, needs_review (moderation flags)
├── email (uploader, optional)
└── date (auto)

Result (1:1 with Video, auto-created via signal)
├── total_votes, stroke, let, no_let (counters)

VoteUser (one per user per video)
├── vote (stroke | let | nolet)
├── video FK, user FK (nullable), session_id
└── UniqueConstraint(video, session_id)

Comment (threaded, self-referencing)
├── parent FK (null = root comment)
├── video FK, user FK (nullable), session_id
├── comment text, created_at

CommentLike / CommentReport (per comment per session)
```

## Code conventions

- **Python:** 4-space indent, snake_case functions/variables, PascalCase models
- **Templates:** 2-space indent, utilities via Tailwind classes, no custom CSS per-template
- **URLs:** lowercase, underscores, verb-object naming: `post_comment`, `like_comment`
- **Commits:** informal, descriptive. No strict conventional commits.
- **No linting/formatting tools configured.** No pre-commit hooks.
- **Tests:** `vote/tests.py` (vote-app suite) + `vote/test_moderation.py`. Run them under **Python 3.13** (`python manage.py test`); the 3.14 `.venv` breaks Django's test client. There is no CI test runner — CI only deploys.
- **Comments in code:** minimal. Code should be self-documenting. Remove debug prints before committing.

## Deployment

- **CI/CD:** `.github/workflows/fly-deploy.yml` auto-deploys on push to `main`
- **Docker:** Python 3.13-slim, collectstatic at build time, gunicorn with 2 workers
- **Fly.io:** release command runs `migrate --noinput`, 1 shared CPU, 1GB RAM
- **Domain:** squashvote.wtf (enforced by CanonicalUrlMiddleware)
- **HTTPS:** enforced by Fly.io reverse proxy

## Environment variables

```
SECRET_KEY          # Django secret key
DEBUG               # True for dev, False for prod
DATABASE_URL        # sqlite:///db.sqlite3 (dev) or postgres://... (prod)
GOOGLE_CLIENT_SECRET # YouTube API OAuth
GOOGLE_CLIENT_ID     # YouTube API OAuth
GOOGLE_AUTH_URI      # https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI     # https://oauth2.googleapis.com/token
REFRESH_TOKEN        # YouTube API refresh token
GOOGLE_API           # YouTube Data API key
```

## Design direction (redesign)

> **Status (2026-06-13): the redesign is implemented and shipped to PRs** against
> `yoyocatw/main` — see Contribution workflow below. The specs in this section are
> the design intent; the code on `uiux-redesign` is the source of truth. See
> `HANDOVER.md` for the full delivery state, open PRs, and gotchas.

This branch (`uiux-redesign`) is a full UI/UX reimagination. Key docs:

- `docs/PRODUCT.md` — Who it's for, what it's NOT, how it should feel
- `docs/BRAND.md` — Voice, tone, visual identity guidelines
- `docs/DESIGN_SYSTEM.md` — Typography, color, spacing, component specs

**Core principles:** Opinionated. Informed. Sharp. Polymarket clarity, subreddit energy. No decoration for decoration's sake. The clip is evidence; the verdict is the point.

### Three finalized screens

Designs finalized in Paper (paper.design). The user flow is: Homepage → Browse → Clip.

**1. Homepage (Hero Landing)**
- Full-bleed hero image (static, stored in `static/images/`) + dark gradient overlay
- Hero text: "The crowd's verdict on controversial calls."
- Subtext: "Watch the clip. Make your call. See where you stand."
- CTA: "Make Your Call →" links to `/browse/`
- "New this week" section: horizontal scrolling clip cards (date < 7 days)
- Photo credit attribution at bottom of hero
- Dark background (#0A0A0A)

**2. Library / Browse (NEW page at `/browse/`)**
- Full-bleed background image (Elias vs Asal, static) + dark gradient overlay
- "All Decisions" heading + "You've voted on X of Y decisions" counter
- Filter tabs: All | PSA | Amateur | Unvoted (HTMX-powered)
- Compact list rows: thumbnail + play icon | title + vote count + badges | chevron
- Badges: category (PSA/Amateur), "Voted" (session check), "NEW" (< 7 days)
- Pagination: 15 per page
- Absorbs the old homepage's filter/sort/pagination logic

**3. Clip (Vote + Results)**
- Full-bleed background from YouTube thumbnail (`maxresdefault.jpg` + blur + overlay)
- Plyr video player at top (plays the clip window once, then a Replay overlay)
- Title + metadata (votes, category badge)
- Vote form: Stroke / Let / No Let radio options (no emoji, custom styled)
- Post-vote reveal: "YOUR CALL" / "THE REF SAID" verdict cards
- CSS horizontal bar chart (replaces Chart.js): server-computed percentages
- Comments section (gated behind vote, keep HTMX patterns)
- "Next One →" CTA at bottom (newest unvoted clip; "Browse all" fallback on the last clip)
- "More decisions" suggestions list (upstream's recommendation feature, restyled)

### Implementation decisions

| Area | Decision |
|------|----------|
| Background images | Static files for homepage/browse; dynamic YouTube thumbs for clips |
| Vote results | Pure CSS/HTML bars — drop Chart.js entirely |
| Navigation | Minimal header: back arrow / "SquashVote.wtf" / hamburger menu |
| Fonts | Add Space Grotesk for headings; keep Bebas Neue (logo), Inter (body) |
| "Unvoted" filter | Exclude videos where session has a VoteUser record |
| "Next Decision" | `get_next_decision()`: newest unvoted clip, simple query |
| DaisyUI | Keep theme system for CSS vars; custom styling on redesigned screens |

### Contribution workflow

- **Upstream:** `origin` → `https://github.com/yoyocatw/SquashVote` (main repo, the live site)
- **Fork:** `fork` → `https://github.com/SpunkyMartian/SquashVote` (PR branches live here)
- **Branch:** `uiux-redesign` (canonical local dev branch; push topic branches to fork, PR against origin/main)
- **CI/CD:** Push to `main` on origin auto-deploys to Fly.io via GitHub Actions — so **never merge a partial/broken change**; `main` must always be deployable.

**Open PRs (as of 2026-06-13)** — all independent & mergeable; see `HANDOVER.md`:
- **#2** `redesign/docs` — docs / design system (docs only)
- **#3** `redesign/app` — the redesign + tests + review fixes
- **#4** `fix/comment-user-default` — `default="Anonymous"` FK bug + migration
- **#5** `fix/moderation-auth` — gate accept/reject video actions (security)

The redesign implementation is **atomic for deploy** (theme/chrome/screens/backend
depend on each other) — only docs separates cleanly; don't try to split #3 further.

### Do NOT

- Add new Python dependencies without discussion
- Change model fields casually. (The clip-window feature is a deliberate exception:
  it added the optional `Video.end_timestamp` field + migration `0006`. Anything
  beyond that still needs discussion.)
- Remove any existing URL routes (backward compat)
- Use class-based views
- Add loading spinners or skeleton screens
- Use emoji in UI copy
- Add rounded corners > 12px
- Add shadows on cards/buttons
