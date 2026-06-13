from django import forms
from .models import Video, MIN_CLIP_SECONDS, MAX_CLIP_SECONDS
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path.lstrip('/')
    return None


def parse_timestamp(value):
    """Parse 'M:SS' / 'H:MM:SS' (or plain seconds) into an int, or None if invalid."""
    if not value:
        return None
    try:
        return Video.convert_timestamp_to_seconds(value.strip())
    except (ValueError, AttributeError):
        return None

class VideoForm(forms.ModelForm):
    youtube_url = forms.URLField(label="YouTube URL")

    class Meta:
        model = Video
        fields = ["email", "timestamp", "end_timestamp", "org_decision", "category"]

    def clean(self):
        cleaned = super().clean()
        url = cleaned.get("youtube_url")
        if url:
            video_id = extract_video_id(url)
            if not video_id:
                raise forms.ValidationError("Invalid YouTube URL.")
            cleaned["video_id"] = video_id

        start = parse_timestamp(cleaned.get("timestamp"))
        if cleaned.get("timestamp") and start is None:
            self.add_error("timestamp", "Use a timestamp like 4:20 or 1:06:09.")

        end_raw = cleaned.get("end_timestamp")
        if end_raw:
            end = parse_timestamp(end_raw)
            if end is None:
                self.add_error("end_timestamp", "Use a timestamp like 4:35 or 1:06:25.")
            elif start is not None:
                length = end - start
                if length <= 0:
                    self.add_error("end_timestamp", "The end must come after the start timestamp.")
                elif length < MIN_CLIP_SECONDS:
                    self.add_error("end_timestamp", f"Clip is too short — make it at least {MIN_CLIP_SECONDS}s.")
                elif length > MAX_CLIP_SECONDS:
                    self.add_error("end_timestamp", f"Clip is too long — keep it under {MAX_CLIP_SECONDS}s.")
        return cleaned


VOTE_CHOICES = [
    ("stroke", "Stroke"),
    ("let", "Let"),
    ("nolet", "No Let"),
]


class VoteForm(forms.Form):
    vote = forms.ChoiceField(choices=VOTE_CHOICES, widget=forms.RadioSelect)

# forms.py
from django import forms

class CommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'What are your thoughts?'}),
        label=''
    )
