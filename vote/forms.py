from django import forms
from .models import Video
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path.lstrip('/')
    return None

class VideoForm(forms.ModelForm):
    youtube_url = forms.URLField(label="YouTube URL")

    class Meta:
        model = Video
        fields = ["email", "timestamp", "org_decision", "category"]

    def clean(self):
        cleaned = super().clean()
        url = cleaned.get("youtube_url")
        if url:
            video_id = extract_video_id(url)
            if not video_id:
                raise forms.ValidationError("Invalid YouTube URL.")
            cleaned["video_id"] = video_id
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
