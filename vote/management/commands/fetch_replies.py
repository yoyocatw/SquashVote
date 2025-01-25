from django.core.management import BaseCommand
from vote.client.youtube_client import youtube_client
from collections import Counter
from vote.models import Video, Result


class Command(BaseCommand):

    def handle(self, *args, **options):
        youtube = youtube_client()
        active_video = Video.objects.filter(is_active=True, is_posted=True).exclude(
            comment_id__isnull=True
        )

        for video in active_video:
            request = youtube.comments().list(part="snippet", parentId=video.comment_id)
            response = request.execute()
            replies = []
            for item in response.get("items", []):
                reply_text = item["snippet"]["textOriginal"]
                replies.append(reply_text)

            decisions = {"1": "stroke", "2": "let", "3": "no_let"}
            result = []
            for reply in replies:
                clean_reply = reply.strip().lower()
                if clean_reply in decisions:
                    result.append(decisions[clean_reply])

            total_votes = len(result)
            if total_votes != 0:
                vote_amount = Counter(result)
                stroke_count = vote_amount.get("stroke", 0)
                let_count = vote_amount.get("let", 0)
                no_let_count = vote_amount.get("no_let", 0)

                results, created = Result.objects.get_or_create(video=video)

                if total_votes > results.total_votes:

                    results.total_votes = total_votes
                    results.stroke = stroke_count
                    results.let = let_count
                    results.no_let = no_let_count
                    results.save()

                    self.stdout.write(
                        self.style.SUCCESS(f"Fetched replies for {video.video_id}")
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Total Votes: {total_votes}, Stroke: {stroke_count}, Let: {let_count}, No Let: {no_let_count}"
                        )
                    )
                    stroke_percentage = (stroke_count / total_votes) * 100
                    let_percentage = (let_count / total_votes) * 100
                    no_let_percentage = (no_let_count / total_votes) * 100
                    percentages = {
                        "stroke": stroke_percentage,
                        "let": let_percentage,
                        "no_let": no_let_percentage,
                    }

                    comment = (
                        f"{video.timestamp} *What is your decision?*\n"
                        "Reply: [ 1 for *Stroke* ], [ 2 for *Let* ], [ 3 for *No Let* ]\n"
                        "Results👇\n"
                        f"({total_votes} votes)\n\n"
                        f"Stroke    {percentages['stroke']:>3.0f}% ({results.stroke})\n"
                        f"Let       {percentages['let']:>3.0f}% ({results.let})\n"
                        f"No let    {percentages['no_let']:>3.0f}% ({results.no_let})"
                    )
                    request = youtube.comments().update(
                        part="snippet",
                        body={
                            "id": video.comment_id,
                            "snippet": {"textOriginal": comment},
                        },
                    )
                    response = request.execute()

                    self.stdout.write(self.style.SUCCESS(f"Comment Updated #######"))
                    stroke_percentage = (stroke_count / total_votes) * 100
                else:
                    print("There is no new votes")
            else:
                vote_amount = {"stroke": 0, "let": 0, "no_let": 0}
                print("There are no votes")
                # percentages = {"stroke": 0, "let": 0, "no_let": 0}
