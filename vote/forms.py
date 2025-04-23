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

# forms.py
from django import forms

class CommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'What are your thoughts?'}),
        label=''
    )
