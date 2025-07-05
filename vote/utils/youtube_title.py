import re
from googleapiclient.discovery import build
from django.conf import settings


def get_youtube_title(url):
    # Extract video ID from URL
    match = re.search(r"(?:v=|youtu\.be/)([\w\-]+)", url)
    if not match:
        raise ValueError("Invalid YouTube URL")
    video_id = match.group(1)

    youtube = build("youtube", "v3", developerKey=settings.GOOGLE_API)
    request = youtube.videos().list(part="snippet", id=video_id)
    response = request.execute()

    items = response.get("items")
    if not items:
        raise ValueError("Video not found")

    return items[0]["snippet"]["title"]