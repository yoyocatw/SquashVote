# SquashVote.WTF ✊
[![forthebadge](https://forthebadge.com/api/badges/generate?panels=2&primaryLabel=6&secondaryLabel=7&primaryBGColor=%2331C4F3&primaryTextColor=%23FFFFFF&secondaryBGColor=%23389AD5&secondaryTextColor=%23FFFFFF&primaryFontSize=12&primaryFontWeight=600&primaryLetterSpacing=2&primaryFontFamily=Roboto&primaryTextTransform=uppercase&secondaryFontSize=12&secondaryFontWeight=900&secondaryLetterSpacing=2&secondaryFontFamily=Montserrat&secondaryTextTransform=uppercase)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/0-percent-optimized.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg)](https://forthebadge.com)

[![forthebadge](https://forthebadge.com/images/badges/you-didnt-ask-for-this.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/badges/built-with-love.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/badges/it-works-why.svg)](https://forthebadge.com)



**SquashVote.wtf** is a full-stack web app that lets squash fans vote on controversial referee decisions.

Ever watched a squash match and thought:

>"That's definitely a Stroke."

Then the referee gives a No Let.
And your brain goes WTF...

Now you can see if you weren't the only one.


## Live Site
[https://squashvote.wtf](https://squashvote.wtf)

## Features

- **Vote**: Cast your vote on controversial referee decisions. Instantly see the percentage of fans who agree (or disagree) with you.

- **Upload Your Own Video**: See a questionable call in a YouTube video or your own match? Upload it and get the community’s opinion.

## Tech Stack
Frontend: HTMX, Alpine.js, Tailwind CSS

Backend: Django

Database: PostgreSQL

Deployment: Fly.io

## Local Development

To run the project locally, you need to edit your squashvote/settings.py file. Follow these steps:

1. Update Allowed Hosts
Add 127.0.0.1 or your local host URL to ALLOWED_HOSTS.

```python
ALLOWED_HOSTS = [
    "squashvote.wtf",
    "www.squashvote.wtf",
    "squashvote.fly.dev",
    "127.0.0.1",
    "localhost"
]
```
2. Configure Secure Cookies
Set session and CSRF cookies to False for local development. 

```python
# Change to False for local development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Keep as True for production, make sure these are True in production.
SESSION_COOKIE_SECURE = True 
CSRF_COOKIE_SECURE = True
```
3. Remove Canonical URL Middleware
Comment out or remove CanonicalUrlMiddleware to prevent routing errors locally.

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # "vote.middleware.CanonicalUrlMiddleware",  <-- Remove or comment out for local development
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```
