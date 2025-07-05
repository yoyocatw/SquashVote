from django.shortcuts import render, redirect, get_object_or_404
from .forms import VideoForm, VoteForm, CommentForm
from .models import Video, VoteUser, Comment, CommentReport, CommentLike
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from .utils.youtube_title import get_youtube_title

# Create your views here.
def get_session_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def index(request):
    videos = Video.objects.filter(is_active=True, needs_review=False).select_related(
        "result"
    )
    # Category videos
    category = request.GET.get("category", "all")
    if category != "all":
        videos = videos.filter(category__iexact=category)
    # Sorting Videos
    sorted_by = request.GET.get("sort", "newest")
    if sorted_by == "most_votes":
        videos = videos.order_by("-result__total_votes")
    elif sorted_by == "oldest":
        videos = videos.order_by("date")
    else:
        videos = videos.order_by("-date")

    paginator = Paginator(videos, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "videos": videos,
        "sorted_by": sorted_by,
        "category": category,
        "page_obj": page_obj,
    }
    #HTMX reload
    if request.headers.get("HX-Request"):
        return render(
            request,
            "vote/partials/video_grid.html",
            context,
        )
    # Full page reload
    return render(request, "vote/index.html", context=context)


def user_already_voted(request, video):
    if request.user.is_authenticated:
        vote = VoteUser.objects.filter(user=request.user, video=video).first()
    else:
        session_id = get_session_id(request)
        vote = VoteUser.objects.filter(session_id=session_id, video=video).first()

    return (vote is not None, vote.vote if vote else None)


def video_result(request, pk, slug=None):
    video = get_object_or_404(Video.objects.select_related("result"), pk=pk)
    start = Video.convert_timestamp_to_seconds(video.timestamp)
    already_voted, vote = user_already_voted(request, video)
    session_id = get_session_id(request)

    # Deal with what user voted for Stroke, Let, No Let
    if request.method == "POST":
        form = VoteForm(request.POST)
        if form.is_valid():
            vote = form.cleaned_data["vote"]
            _, created = VoteUser.objects.get_or_create(
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                video=video,
                defaults={"vote": vote},
            )
            if created:
                video.result.total_votes += 1
                if vote == "stroke":
                    video.result.stroke += 1
                elif vote == "let":
                    video.result.let += 1
                elif vote == "nolet":
                    video.result.no_let += 1
                video.result.save()

            response = render(
                request,
                "vote/partials/already_voted.html",
                context={"vote": vote, "video": video},
            )
            return response
    else:
        form = VoteForm()
    # Sorting comments
    sort_by = request.GET.get("sort", "upvotes")
    comments = Comment.objects.filter(video=video, parent=None).annotate(
        num_likes=Count("likes")
    )

    if sort_by == "newest":
        comments = comments.order_by("-created_at")
    elif sort_by == "oldest":
        comments = comments.order_by("created_at")
    else:  # sort by most liked
        comments = comments.order_by("-num_likes")

    # Return a list of comments that the user already upvoted (reload)
    liked_comments = CommentLike.objects.filter(
        session_id=session_id, comment__video__video_id=video.video_id
    ).values_list("comment_id", flat=True)
    reported = CommentReport.objects.filter(
        session_id=session_id, comment__video__video_id=video.video_id
    ).values_list("comment_id", flat=True)

    # HTMX paritals return
    if request.method == "GET" and "sort" in request.GET:
        return render(
            request,
            "vote/partials/comment_section.html",
            {
                "video": video,
                "comments": comments,
                "liked_comments": list(liked_comments),
                "sort_by": sort_by,
                "reported": list(reported),
            },
        )
    # Full page reload
    context = {
        "video": video,
        "already_voted": already_voted,
        "vote": vote,
        "start": start,
        "comments": comments,
        "liked_comments": list(liked_comments),
        "reported": list(reported),
        "sort_by": sort_by,
    }
    return render(request, "vote/video_result.html", context=context)


def chart(request, pk):
    video = get_object_or_404(Video.objects.select_related("result"), pk=pk)
    data = {
        "labels": ["Stroke", "Let", "No Let"],
        "data": [
            int(video.result.stroke),
            int(video.result.let),
            int(video.result.no_let),
        ],
    }
    return JsonResponse(data)

def video_form(request):
    if request.method == "POST":
        form = VideoForm(request.POST)
        if form.is_valid():
            video = form.save(commit=False)
            video.video_id = form.cleaned_data["video_id"]
            url = form.cleaned_data["youtube_url"]
            video.video_title = get_youtube_title(url)
            video.is_active = False
            video.save()
            return redirect("confirm")
    else:
        form = VideoForm()

    return render(request, "vote/video_form.html", {"form": form})


def confirm(request):
    return render(request, "vote/confirm.html")


@login_required
def review(request):
    videos = Video.objects.filter(needs_review=True).order_by("date")

    for video in videos:
        duplicates = []
        same_id = Video.objects.filter(video_id=video.video_id).exclude(id=video.id)
        for dup in same_id:  # 👈 don't use 'video' again here
            duplicates.append(dup)
        video.same_id = duplicates

    return render(request, "vote/review.html", {"videos": videos})


def accept_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    video.is_active = True
    video.needs_review = False
    video.save()
    return HttpResponse("Accepted")


def reject_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    video.delete()
    return HttpResponse("Rejected")


def about(request):
    return render(request, "vote/about.html")


def rules(request):
    return render(request, "vote/squashrules.html")


def post_comment(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment.objects.create(
                video=video,
                user=request.user if request.user.is_authenticated else None,
                comment=form.cleaned_data["comment"],
                parent=None,
            )
            comments = Comment.objects.filter(video=video, parent=None).order_by(
                "-created_at"
            )
            return render(
                request,
                "vote/partials/comment_section.html",
                {"video": video, "comments": comments},
            )
    else:
        form = CommentForm()
    comments = Comment.objects.filter(video=video).order_by("-created_at")
    return render(
        request, "vote/video_result.html", {"form": form, "comments": comments}
    )


# When user clicks like (instantly)
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    voted = False
    session_id = get_session_id(request)

    if request.method == "POST":

        like_record = CommentLike.objects.filter(
            comment=comment, session_id=session_id
        ).first()

        if like_record:
            like_record.delete()
            voted = False
        else:
            CommentLike.objects.create(comment=comment, session_id=session_id)
            voted = True

        num_likes = comment.likes.count()

        return render(
            request,
            "vote/partials/like_comment.html",
            {
                "comment": comment,
                "voted": voted,
                "num_likes": num_likes,
            },
        )

    return HttpResponseNotAllowed(["POST"])


def post_reply(request, comment_id):
    if request.method == "POST":
        parent = get_object_or_404(Comment, id=comment_id)
        content = request.POST.get("reply_content")

        if content:
            reply = Comment.objects.create(
                comment=content,
                parent=parent,
                video=parent.video,
                user=request.user if request.user.is_authenticated else None,
            )
            reply.save()

            return render(request, "vote/partials/replies.html", {"reply": reply})

    return HttpResponse(status=400)


def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    reported = False
    session_id = get_session_id(request)

    if request.method == "POST":
        reporttracker = CommentReport.objects.create(
            comment=comment,
            user=request.user if request.user.is_authenticated else None,
            session_id=(
                request.session.session_key
                if not request.user.is_authenticated
                else None
            ),
        )

        reported = True

        reporttracker.save()

        return render(
            request,
            "vote/partials/report.html",
            {"comment": comment, "reported": reported},
        )

    return HttpResponseNotAllowed(["POST"])
