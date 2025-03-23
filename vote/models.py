from django.db import models
from datetime import date
from django.utils.timezone import now
from django.contrib.auth.models import User


# Create your models here.
class Video(models.Model):
    class Decision(models.TextChoices):
        STROKE = "Stroke"
        LET = "Let"
        NO_LET = "No Let"

    date = models.DateField(default=date.today)
    video_title = models.CharField(max_length=500)
    timestamp = models.CharField(max_length=50)
    video_id = models.CharField(max_length=512, unique=True)
    org_decision = models.CharField(max_length=20, choices=Decision.choices)
    is_active = models.BooleanField(default=True)

    def convert_timestamp_to_seconds(timestamp):
        parts = timestamp.split(":")
        if len(parts) == 2:  # For minutes and seconds
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # For hours minutes and seconds
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0

    def create_url(self):
        seconds = Video.convert_timestamp_to_seconds(self.timestamp)
        end_seconds = seconds + 30
        return f"https://www.youtube-nocookie.com/embed/{self.video_id}?start={seconds}&end={str(end_seconds)}&autoplay=0&modestbranding=1&rel=0&controls=0"
    def go_to_youtube(self):
        seconds = Video.convert_timestamp_to_seconds(self.timestamp)
        return f"https://www.youtube.com/watch?v={self.video_id}&t={seconds}"
    

    def __str__(self):
        return f"{self.video_title} - {self.video_id} - {self.org_decision}"


class Result(models.Model):
    video = models.OneToOneField(Video, on_delete=models.CASCADE)
    total_votes = models.IntegerField(default=0)
    stroke = models.IntegerField(default=0)
    let = models.IntegerField(default=0)
    no_let = models.IntegerField(default=0)

    def __str__(self):
        return f"Votes for {self.video.video_title}: Stroke-{self.stroke}, Let-{self.let}, No Let-{self.no_let}"


class VoteUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    vote = models.CharField(
        max_length=20,
        choices=[("let", "Let"), ("stroke", "Stroke"), ("nolet", "No Let")],
    )
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        unique_together = ("video", "user")

    def __str__(self):
        return f"{self.user} voted {self.vote} for {self.video.video_title}"
