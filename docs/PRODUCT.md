# SquashVote — Product Identity

## What is this?

SquashVote is the crowd's verdict on controversial squash referee decisions. It's a permanent, accumulating consensus — not a poll that disappears after a day.

The pitch: **"It settles arguments."**

---

## Who is this for?

The person who watches a PSA match, sees a controversial call, and immediately wants to argue about it.

They know what interference is. They know the difference between a let and a stroke. They've had the "he wasn't making every effort to clear" argument at their local club. They might referee at amateur level themselves. They're on r/squash, they follow PSA World Tour, they've watched Willstrop's old videos explaining the rules.

This is **not** for someone who needs to learn what a let is. The site doesn't explain itself. It assumes competence. If you don't understand the options, you're not the audience, and that's fine.

**Real-world analogy:** The football fan who pauses the TV, draws an offside line with their finger, and says "his shoulder is clearly on." Except in squash, these calls are genuinely subjective — which makes the debate more interesting and more legitimate.

---

## What it's definitely NOT

### Not a highlights platform
This isn't about great rallies or spectacular shots. If the rally ended cleanly, it doesn't belong here. The only content that matters is moments where a decision was made and someone could reasonably disagree.

### Not educational
There's no "learn the rules" section, no beginner's guide to interference. Designing for beginners now dilutes the voice. The tone assumes you already care and already know.

### Not a social network
You don't need profiles with bios and followers. Nobody is here to build an audience. They're here to make a call and see if others agree. Identity is secondary to judgment.

### Not trying to look like ESPN or Sky Sports
No dark gradients, no swooshy graphics, no "BREAKING" energy. That aesthetic is performative. The audience sees through it and finds it corny.

### Not a video app
The video is a means to an end. The clip is evidence; the verdict is the point. If someone spends more time watching than voting and reading arguments, something is wrong.

### Not gamified
No points, badges, leaderboards, streaks. The calls ARE the content. Don't wrap them in a meta-game that becomes more important than the actual decisions.

---

## How it feels

A courtroom crossed with a pub argument.

There's a formal structure — here's the clip, here are your options, here's what the ref called, here's what the crowd thinks — but the energy underneath is informal and opinionated. You see the clip, you make your call, and then you get to see whether you're in the majority or the contrarian.

**Closest digital analogy:** Polymarket's clarity and information density, crossed with the communal energy of a subreddit thread. Clean, confident, no decoration for decoration's sake. The UI respects your time and your knowledge of the sport.

**Personality in three words:** Opinionated. Informed. Sharp.

Not warm. Not playful. Not corporate. Not slick.

Just: "here's the call, what's yours?"

---

## Content philosophy

- Content-driven. No new clips = no reason to visit, and that's okay.
- Don't manufacture engagement when there's nothing new.
- Focus energy on making each new clip moment great.
- Only controversial decisions. If the call was obviously correct, it doesn't belong.

---

## Core user journey

1. User arrives (usually via a shared link on Reddit/WhatsApp to a specific clip)
2. Watches the clip — the video is evidence, not entertainment
3. Makes their call (Stroke / Let / No Let)
4. Sees the reveal: what the ref said, what the community thinks
5. Reads the arguments, maybe drops their own take in the comments
6. Hits "Next" — smart queue serves them the most relevant unvoted clip
7. After a few clips (5-10 min), they're satisfied and leave

---

## Key decisions (redesign)

| Area | Decision |
|------|----------|
| Layout | Compact card — video + vote + results + comments, minimal scrolling |
| Homepage | Minimal — CTA to start voting + "new this week" clips |
| Post-vote flow | Show results & comments, then explicit "Next" button |
| Next clip algo | Smart queue: newest first, then most split votes, then least voted |
| Comments | Gated behind vote (prevents anchoring bias) |
| Accounts | Anonymous. No login. Session-based. |
| Traffic | Mostly mobile, via shared clip links |
| Visual tone | Clean, dense, utilitarian. Polymarket, not ESPN. |
