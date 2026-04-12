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
# Edit .env with your values (DATABASE_URL, SECRET_KEY, Google API keys)

# Local dev settings changes needed in squashvote/settings.py:
# - Add '127.0.0.1' and 'localhost' to ALLOWED_HOSTS
# - Set SESSION_COOKIE_SECURE = False
# - Set CSRF_COOKIE_SECURE = False
# - Comment out 'vote.middleware.CanonicalUrlMiddleware' in MIDDLEWARE

# Run database migrations
python manage.py migrate

# Start CSS watcher (terminal 1)
npm run dev

# Start Django dev server (terminal 2)
python manage.py runserver
```

## Tech stack

- **Backend:** Django 5.1.5, Python 3.13
- **Frontend:** HTMX 2.0.4, Alpine.js 3.14.8, Tailwind CSS 4.1.11, DaisyUI 5.0.0-beta.2
- **Video:** Plyr 3.8.3 wrapping YouTube embeds (20s clip window)
- **Charts:** Chart.js 4.4.9
- **Database:** PostgreSQL (prod), SQLite (dev)
- **Deployment:** Fly.io (Docker, gunicorn, SJC region)
- **Static files:** WhiteNoise
- **Analytics:** Plausible

## Project structure

```
squashvote/          # Django project settings (settings.py, urls.py, wsgi.py)
vote/                # Main app — all application code lives here
  models.py          # Video, Result, VoteUser, Comment, CommentLike, CommentReport
  views.py           # All views (function-based, never CBV)
  forms.py           # VideoForm, VoteForm, CommentForm
  urls.py            # App routes
  signals.py         # post_save: auto-create Result when Video created
  middleware.py      # CanonicalUrlMiddleware (domain redirect)
  admin.py           # Custom admin with reported comment actions
  templatetags/      # timestamp.py — comment_time filter (relative dates)
  utils/             # youtube_title.py — fetch title via Google API
  templates/vote/    # Full page templates
  templates/vote/partials/  # HTMX partial templates
static/
  css/input.css      # Tailwind source (themes, fonts, utilities)
  css/output.css     # Compiled CSS (run npm run dev to rebuild)
  js/                # chart.js, confetti.js, plyr.js, modal.js, etc.
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
| Tests | `python manage.py test` |
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
- Chart.js uses `MutationObserver` on `data-theme` to update colors dynamically
- Theme toggle uses `theme-change` library with checkbox `.theme-controller`

### Plyr video player
- Clips play a 20-second window from `start` to `start + 20`
- Auto-loops, snaps to start on seek
- Starts muted (autoplay policy), unmutes on first click

## Data model

```
Video (the clip/decision)
├── video_id (YouTube ID)
├── video_title (fetched from YouTube API)
├── timestamp → converted to start seconds
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
- **No tests currently.** `vote/tests.py` is a placeholder.
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

## Design direction (current redesign)

This branch (`Anvith-Reddy-N/uiux-redesign`) is a full UI/UX reimagination. Key docs:

- `docs/PRODUCT.md` — Who it's for, what it's NOT, how it should feel
- `docs/BRAND.md` — Voice, tone, visual identity guidelines
- `docs/DESIGN_SYSTEM.md` — Typography, color, spacing, component specs

**Core principles:** Opinionated. Informed. Sharp. Polymarket clarity, subreddit energy. No decoration for decoration's sake. The clip is evidence; the verdict is the point.
