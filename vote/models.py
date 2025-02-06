from django.db import models
from datetime import date
from django.utils.timezone import now


# Create your models here.
class Video(models.Model):
    class Decision(models.TextChoices):
        STROKE = "Stroke"
        LET = "Let"
        NO_LET = "No Let"

    date = models.DateField(default=date.today)
    video_title = models.CharField(max_length=500)
    timestamp = models.CharField(max_length=50)
    video_id = models.CharField(max_length=255)
    comment_id = models.CharField(max_length=255, null=True, blank=True)
    org_decision = models.CharField(max_length=20, choices=Decision.choices)
    is_posted = models.BooleanField(default=False)
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
        return f"https://www.youtube.com/embed/{self.video_id}?start={seconds}&modestbranding=1&rel=0"

    def comment_url(self):
        return f"https://www.youtube.com/watch?v={self.video_id}&lc={self.comment_id}"

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


class YoutubeQuota(models.Model):
    date = models.DateField(default=now, unique=True)
    quota = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.date}: {self.quota} api quota use"

class VoteUser(models.Model):
    youtube_user_id = models.CharField(max_length=255)
    vote = models.CharField(max_length=20, choices=Video.Decision.choices)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('video', 'youtube_user_id')
    def __str__(self):
        return f"{self.user_id} voted {self.vote} for {self.video.video_title}"