from django.core.management.base import BaseCommand
from vote.models import Video, Result
from vote.client.youtube_client import youtube_client


class Command(BaseCommand):
    help = "Post a comment to Youtube"

    def handle(self, *args, **options):
        youtube = youtube_client()
        not_posted = Video.objects.filter(is_posted=False, comment_id__isnull=True)
        if not_posted.exists():
            for video in not_posted:
                print("Posting Comment ######")
                comment = (
                    f"{video.timestamp} *What is your decision?*\n"
                    "Reply: [ 1 for *Stroke* ], [ 2 for *Let* ], [ 3 for *No Let* ]\n"
                    "Results👇\n"
                    "(0 votes)\n\n"
                    "Stroke     0%\n"
                    "Let    0%\n"
                    "No let     0%\n\n"
                    "Learn More: (link)"
                )

                request = youtube.commentThreads().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "videoId": video.video_id,
                            "topLevelComment": {"snippet": {"textOriginal": comment}},
                        }
                    },
                )
                response = request.execute()
                video.comment_id = response["id"]
                video.is_posted = True
                video.save()
                print("Comment Posted :)")
                self.stdout.write(
                    self.style.SUCCESS(f"Comment posted on {video.video_id}")
                )
                return response.get("id")
        else:
            print("No videos")
