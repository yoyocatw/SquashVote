from django.shortcuts import render, redirect, get_object_or_404
from .forms import VideoForm, VoteForm, CommentForm
from .models import Video, VoteUser, Comment, CommentReport, CommentLike
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .utils.youtube_title import get_youtube_title


def get_session_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_voted_video_ids(session_id):
    """Set of video ids this session has voted on."""
    return set(
        VoteUser.objects.filter(session_id=session_id).values_list("video_id", flat=True)
    )


def vote_percentages(result):
    """Server-computed Stroke/Let/No Let percentages for the CSS bars."""
    total = result.total_votes or 1
    return {
        "stroke_pct": round(result.stroke / total * 100),
        "let_pct": round(result.let / total * 100),
        "nolet_pct": round(result.no_let / total * 100),
    }


def get_next_decision(request, current_video):
    """Return the newest unvoted clip and fresh unvoted count (last 30 days)."""
    session_id = get_session_id(request)
    voted_ids = get_voted_video_ids(session_id)

    unvoted = (
        Video.objects.filter(is_active=True, needs_review=False)
        .exclude(id__in=voted_ids)
        .exclude(id=current_video.id)
        .select_related("result")
        .order_by("-date")
    )

    one_month_ago = timezone.now() - timedelta(days=30)
    fresh_count = unvoted.filter(date__gte=one_month_ago).count()

    return unvoted.first(), fresh_count


def index(request):
    one_week_ago = timezone.now() - timedelta(days=7)

    new_this_week = (
        Video.objects.filter(
            is_active=True, needs_review=False, date__gte=one_week_ago
        )
        .select_related("result")
        .order_by("-date")[:8]
    )

    # Fallback if fewer than 3 new clips this week
    if new_this_week.count() < 3:
        new_this_week = (
            Video.objects.filter(is_active=True, needs_review=False)
            .select_related("result")
            .order_by("-date")[:8]
        )
        section_title = "Latest decisions"
    else:
        section_title = "New this week"

    total_decisions = Video.objects.filter(
        is_active=True, needs_review=False
    ).count()

    context = {
        "new_this_week": new_this_week,
        "section_title": section_title,
        "total_decisions": total_decisions,
    }
    return render(request, "vote/index.html", context=context)


def browse(request):
    session_id = get_session_id(request)

    videos = Video.objects.filter(
        is_active=True, needs_review=False
    ).select_related("result")

    voted_ids = get_voted_video_ids(session_id)

    category = request.GET.get("category", "all")
    if category == "psa":
        videos = videos.filter(category__iexact="PSA")
    elif category == "amateur":
        videos = videos.filter(category__iexact="Amateur")
    elif category == "unvoted":
        videos = videos.exclude(id__in=voted_ids)

    sorted_by = request.GET.get("sort", "newest")
    if sorted_by == "most_votes":
        videos = videos.order_by("-result__total_votes")
    elif sorted_by == "oldest":
        videos = videos.order_by("date")
    else:
        videos = videos.order_by("-date")

    paginator = Paginator(videos, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    total_decisions = Video.objects.filter(
        is_active=True, needs_review=False
    ).count()
    voted_count = len(voted_ids)

    new_cutoff = timezone.now() - timedelta(days=7)

    filter_tabs = [
        ("all", "All"),
        ("psa", "PSA"),
        ("amateur", "Amateur"),
        ("unvoted", "Unvoted"),
    ]

    context = {
        "page_obj": page_obj,
        "category": category,
        "sorted_by": sorted_by,
        "total_decisions": total_decisions,
        "voted_count": voted_count,
        "voted_video_ids": voted_ids,
        "new_cutoff": new_cutoff,
        "filter_tabs": filter_tabs,
        "show_back": True,
        "back_url": "/",
    }

    if request.headers.get("HX-Request"):
        return render(request, "vote/partials/browse_list.html", context)

    return render(request, "vote/browse.html", context=context)


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
                video.result.refresh_from_db()

            pct = vote_percentages(video.result)

            vote_display_map = {"stroke": "Stroke", "let": "Let", "nolet": "No Let"}
            vote_display = vote_display_map.get(vote, "")

            next_video, remaining_count = get_next_decision(request, video)

            # Fetch comments for the post-vote reveal
            post_comments = Comment.objects.filter(video=video, parent=None).annotate(
                num_likes=Count("likes")
            ).order_by("-num_likes")

            liked_comments = CommentLike.objects.filter(
                session_id=session_id, comment__video__video_id=video.video_id
            ).values_list("comment_id", flat=True)
            reported = CommentReport.objects.filter(
                session_id=session_id, comment__video__video_id=video.video_id
            ).values_list("comment_id", flat=True)

            return render(
                request,
                "vote/partials/post_vote.html",
                context={
                    "vote": vote,
                    "vote_display": vote_display,
                    "video": video,
                    **pct,
                    "next_video": next_video,
                    "remaining_count": remaining_count,
                    "comments": post_comments,
                    "liked_comments": list(liked_comments),
                    "reported": list(reported),
                    "sort_by": "upvotes",
                },
            )
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
    
    suggested_videos = (
        Video.objects.filter(is_active=True, needs_review=False)
        .exclude(id=video.id)
        .exclude(id__in=get_voted_video_ids(session_id))
        .select_related("result")
        .order_by("-result__total_votes")[:6]
    )
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
    # Percentage calculations for CSS bars
    pct = vote_percentages(video.result)

    vote_display_map = {"stroke": "Stroke", "let": "Let", "nolet": "No Let"}
    vote_display = vote_display_map.get(vote, "")

    next_video, remaining_count = get_next_decision(request, video)

    # Full page reload
    context = {
        "video": video,
        "already_voted": already_voted,
        "vote": vote,
        "vote_display": vote_display,
        "start": start,
        "comments": comments,
        "liked_comments": list(liked_comments),
        "reported": list(reported),
        "sort_by": sort_by,
        **pct,
        "next_video": next_video,
        "remaining_count": remaining_count,
        "show_back": True,
        "back_url": "/browse/",
        "suggested_videos": suggested_videos,
    }
    return render(request, "vote/video_result.html", context=context)


def video_form(request):
    if request.method == "POST":
        form = VideoForm(request.POST)
        if form.is_valid():
            video = form.save(commit=False)
            video.video_id = form.cleaned_data["video_id"]
            url = form.cleaned_data["youtube_url"]
            video.video_title = get_youtube_title(url)
            video.is_active = True # Set to True for now (bypass review) when more people use site change to False to have review back
            video.needs_review = False # Set to False for now (bypass review) when more people use site change to True to have review back
            video.save()
            return redirect("confirm")
    else:
        form = VideoForm()

    return render(request, "vote/video_form.html", {"form": form, "show_back": True, "back_url": "/"})


def confirm(request):
    return render(request, "vote/confirm.html", {"show_back": True, "back_url": "/"})


@login_required
def review(request):
    videos = Video.objects.filter(needs_review=True).order_by("date")

    for video in videos:
        video.same_id = list(
            Video.objects.filter(video_id=video.video_id).exclude(id=video.id)
        )

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
    return render(request, "vote/about.html", {"show_back": True, "back_url": "/"})


def rules(request):
    return render(request, "vote/squashrules.html", {"show_back": True, "back_url": "/"})


def post_comment(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    video = get_object_or_404(Video, pk=pk)
    session_id = get_session_id(request)

    form = CommentForm(request.POST)
    if form.is_valid():
        Comment.objects.create(
            video=video,
            user=request.user if request.user.is_authenticated else None,
            comment=form.cleaned_data["comment"],
            parent=None,
        )

    # Re-render the thread preserving like/report state and the default
    # (most-liked) order, plus an OOB update of the "N Comments" header.
    comments = (
        Comment.objects.filter(video=video, parent=None)
        .annotate(num_likes=Count("likes"))
        .order_by("-num_likes")
    )
    liked_comments = CommentLike.objects.filter(
        session_id=session_id, comment__video__video_id=video.video_id
    ).values_list("comment_id", flat=True)
    reported = CommentReport.objects.filter(
        session_id=session_id, comment__video__video_id=video.video_id
    ).values_list("comment_id", flat=True)

    return render(
        request,
        "vote/partials/comment_section.html",
        {
            "video": video,
            "comments": comments,
            "liked_comments": list(liked_comments),
            "reported": list(reported),
            "sort_by": "upvotes",
            "update_count": True,
        },
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
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    comment = get_object_or_404(Comment, id=comment_id)
    session_id = get_session_id(request)

    # Idempotent: a repeat report (double-click / replay) must not 500 on the
    # (comment, session_id) unique constraint.
    CommentReport.objects.get_or_create(
        comment=comment,
        session_id=session_id,
        defaults={"user": request.user if request.user.is_authenticated else None},
    )

    return render(
        request,
        "vote/partials/report.html",
        {"comment": comment, "reported": True},
    )


def check_duplicate(request):
    video_id = request.GET.get("video_id")
    videos = Video.objects.filter(video_id=video_id)
    return JsonResponse({
        "exists": videos.exists(),
        "videos": [
            {
                "id": v.pk,
                "title": v.video_title,
                "timestamp": v.timestamp,
                "decision": v.org_decision,
                "category": v.category,
            }
            for v in videos
        ]
    })

def guide(request):
    return render(request, "vote/guide.html", {"show_back": True, "back_url": "/"})


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /superuser/",
        "Disallow: /login/",
        "Disallow: /review/",
        "Disallow: /check-duplicate/",
        "Sitemap: https://squashvote.wtf/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")