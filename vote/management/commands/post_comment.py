from django.core.management.base import BaseCommand
from vote.models import Video, Result, YoutubeQuota
from vote.client.youtube_client import youtube_client
from django.utils.timezone import now
import time
import traceback


class Command(BaseCommand):
    help = "Post a comment to Youtube"

    def handle(self, *args, **options):
        quota, create = YoutubeQuota.objects.get_or_create(
            date=now().date(), defaults={"quota": 0}
        )
        youtube = youtube_client()
        not_posted = Video.objects.filter(is_posted=False, comment_id__isnull=True)
        if not_posted.exists():
            for video in not_posted:
                time.sleep(30)
                if quota.quota + 50 > 10000:
                    self.stdout.write("Quota reached for the day")
                    break
                self.stdout.write("Posting Comment ######")
                comment = (
                    f"{video.timestamp} *What is your decision?*\n"
                    "Reply: [ 1 for *Stroke* ], [ 2 for *Let* ], [ 3 for *No Let* ]\n"
                    "Results👇\n"
                    "(0 votes)\n\n"
                    "Stroke     0%\n"
                    "Let    0%\n"
                    "No let     0%\n\n"
                )
                try:
                    request = youtube.commentThreads().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "videoId": video.video_id,
                                "topLevelComment": {
                                    "snippet": {"textOriginal": comment}
                                },
                            }
                        },
                    )
                    response = request.execute()
                    self.stdout.write("Comment Posted :)")

                    quota.quota += 50
                    quota.save()
                    video.comment_id = response["id"]
                    video.is_posted = True
                    video.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"Comment posted on {video.video_id}")
                    )
                except:
                    self.stdout.write("Cannot Post")
                    traceback.print_exc()

        else:
            self.stdout.write("No videos")
