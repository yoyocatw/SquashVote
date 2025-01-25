from django.db import models
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator


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
