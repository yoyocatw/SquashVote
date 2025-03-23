from django import forms
from .models import Video


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ["video_id", "video_title", "timestamp", "org_decision"]


VOTE_CHOICES = [
    ("stroke", "Stroke"),
    ("let", "Let"),
    ("nolet", "No Let"),
]


class VoteForm(forms.Form):
    vote = forms.ChoiceField(choices=VOTE_CHOICES, widget=forms.RadioSelect)
