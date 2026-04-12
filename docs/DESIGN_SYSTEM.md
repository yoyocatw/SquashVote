# SquashVote — Design System

Reference for all visual decisions. Read BRAND.md first for voice and identity.

---

## Design philosophy

Polymarket's clarity and information density, crossed with the communal energy of a subreddit thread. Every element earns its place by conveying information or enabling action. Nothing decorative.

**Principles:**
1. Information density over whitespace
2. Structure, not decoration
3. Typography does the work
4. Monochrome with purpose — color is reserved for data

---

## Typography

### Typefaces

| Role | Current | Direction |
|------|---------|-----------|
| Logo | Bebas Neue | Keep or evaluate — should feel sharp, not sporty |
| Headings | Montserrat 700/800 | Consider Space Grotesk or Inter — tighter, more utilitarian |
| Body | Inter 400/600 | Keep. Excellent readability at small sizes. |
| UI labels | Inter | Keep |

### Scale

| Element | Size | Weight | Notes |
|---------|------|--------|-------|
| Page heading | 24-28px | 700-800 | Tight letter-spacing (-0.5px) |
| Section heading | 16-18px | 700 | e.g. "Community Results", "Comments" |
| Body text / comments | 14-15px | 400 | line-height: 1.45-1.5 |
| Metadata | 12-13px | 400-500 | Timestamps, vote counts, tags |
| Labels / chips | 11px | 500-600 | Category tags, sort buttons |

### Rules
- No all-caps except very short labels (e.g. "PSA", "YOU VOTED", "REF SAID")
- No display fonts in body content
- No emoji as UI elements in the redesign

---

## Color

### Light mode

| Token | Value | Usage |
|-------|-------|-------|
| Surface | #fafafa | Page background |
| Surface elevated | #ffffff | Cards, inputs |
| Border | #e5e5e5 | Card borders, dividers |
| Text primary | #111111 | Headings, body text |
| Text secondary | #666666 | Metadata, timestamps |
| Text tertiary | #999999 | Placeholders, disabled |
| Interactive | #111111 | Buttons, links |
| Interactive hover | #333333 | Button hover states |

### Dark mode

| Token | Value | Usage |
|-------|-------|-------|
| Surface | #0f0f0f | Page background |
| Surface elevated | #1a1a1a | Cards, inputs |
| Border | #2a2a2a | Card borders, dividers |
| Text primary | #e5e5e5 | Headings, body text |
| Text secondary | #999999 | Metadata, timestamps |
| Text tertiary | #666666 | Placeholders, disabled |
| Interactive | #e5e5e5 | Buttons, links |
| Interactive hover | #cccccc | Button hover states |

### Data colors (vote bars only)

These are the ONLY place where color carries meaning:

| Vote | Value | Notes |
|------|-------|-------|
| Stroke | #111 (light) / #e5e5e5 (dark) | The "winner" bar — highest contrast |
| Let | #888 (light) / #888 (dark) | Middle ground |
| No Let | #ccc (light) / #444 (dark) | Lowest contrast |

Or, if we want to keep the current vote colors for chart distinctiveness:
- Stroke: #EC6B56 (warm red)
- Let: #FFC154 (amber)
- No Let: #6CA0DC (steel blue)

This is an open decision — monochrome bars (Polymarket-style) vs. colored bars (current). Both are valid.

### Color rules
- No colored buttons. Black/white only. Context makes the action clear.
- No colored backgrounds for sections. White/off-white/dark only.
- No gradients. Ever.
- Color appears in data visualization and state indicators only (e.g. your vote vs ref's call).

---

## Spacing

### Base unit: 4px

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Inline gaps, icon-to-text |
| sm | 8px | Tight gaps within a group |
| md | 12px | Between related elements |
| lg | 16px | Between sections, horizontal page padding |
| xl | 20px | Section padding on mobile |
| 2xl | 24px | Between major sections |
| 3xl | 32px | Large section breaks |

### Layout
- Horizontal page padding: 16-20px (mobile), 24-32px (tablet), 40-80px (desktop)
- Card internal padding: 16-20px
- Consistent vertical rhythm between elements

---

## Components

### Buttons

**Primary action** (Vote, Next Decision):
- Background: #111 (light) / #e5e5e5 (dark)
- Text: inverse of background
- Padding: 14px vertical, full-width on mobile
- Border-radius: 8px (not larger — we're utilitarian, not friendly)
- No shadows, no gradients

**Secondary action** (Replay, sort tabs):
- Background: transparent or #f0f0f0
- Text: #555
- Padding: 8px 12px
- Border-radius: 8px

**Text action** (Reply, Report):
- No background, no border
- Text: #999, weight 500
- Hover: #666

### Cards / containers
- Border: 1px solid #e5e5e5 (light) / 1px solid #2a2a2a (dark)
- Border-radius: 8-10px maximum
- No shadows
- No colored backgrounds

### Vote options (radio buttons)
- Border: 1.5px solid #e5e5e5 (unselected), 2px solid #111 (selected)
- Border-radius: 8px
- Padding: 14px 16px
- Selected state: subtle fill or stronger border, not a color change

### Bar chart (vote results)
- Horizontal bars
- Label on left (fixed width), bar on right
- Percentage inside the bar
- Background track: #f0f0f0 (light) / #1a1a1a (dark)
- No Chart.js canvas — consider pure CSS/HTML bars for consistency and simplicity

### Comments
- Light container: 1px border, 10px radius
- Timestamp + like count in top row
- Body text below
- "Reply" as text action at bottom
- Nested replies indented 24px (ml-6)

### Navigation
- Logo left, actions right
- No colored nav. Same surface as page.
- Back arrow on detail pages, not breadcrumbs
- Mobile: hamburger menu or minimal — few enough pages to show inline

---

## Iconography

- Line icons only, 1.5-2px stroke weight
- Monochrome (#666 default, #111 active)
- 16-20px size
- Used sparingly — text labels preferred over icons alone
- No filled icons, no colored icons, no emoji as functional UI

---

## Motion & interaction

- Minimal. No confetti, no celebration animations.
- Page transitions: none (HTMX swaps are instant)
- Hover states: subtle opacity or color shift
- Vote submission: instant swap to results (no loading spinner unless network-slow)
- The speed IS the delight. Fast, sharp, done.

---

## Responsive breakpoints

| Breakpoint | Width | Layout notes |
|------------|-------|--------------|
| Mobile | < 640px | Single column, full-width cards, 16-20px padding |
| Tablet | 640-1024px | Single column, wider cards, more breathing room |
| Desktop | > 1024px | Centered content (max-width 640-720px), generous margins |

Content should never stretch wider than ~720px on desktop. This is a focused, reading-oriented experience — not a dashboard.

---

## What to avoid

- Rounded corners > 12px (too friendly)
- Colored button backgrounds (too attention-seeking)
- Shadows on cards or buttons (too material-design)
- Gradients (too corporate)
- Decorative illustrations or SVGs (too playful)
- Loading skeletons (too app-like — just swap the content)
- Toast notifications (too SaaS)
- Modal dialogs (too disruptive — inline everything)
