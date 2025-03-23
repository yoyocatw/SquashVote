from django.shortcuts import render, redirect, get_object_or_404
from .forms import VideoForm, VoteForm
from .models import Video, VoteUser
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    videos = (
        Video.objects.filter(is_active=True).select_related("result").order_by("-date")
    )
    context = {"videos": videos}
    return render(request, "vote/index.html", context=context)


def user_already_voted(request, video):
    if request.user.is_authenticated:
        vote = VoteUser.objects.filter(user=request.user, video=video).first()
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        vote = VoteUser.objects.filter(session_id=session_id, video=video).first()

    return (vote is not None, vote.vote if vote else None)


def video_result(request, video_id):
    video = get_object_or_404(Video.objects.select_related("result"), video_id=video_id)
    start = Video.convert_timestamp_to_seconds(video.timestamp)
    already_voted, vote = user_already_voted(request, video)

    if request.method == "POST":
        form = VoteForm(request.POST)
        if form.is_valid():
            vote = form.cleaned_data["vote"]
            VoteUser.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_id=(
                    request.session.session_key
                    if not request.user.is_authenticated
                    else None
                ),
                video=video,
                vote=vote,
            )
            video.result.total_votes += 1
            if vote == "stroke":
                video.result.stroke += 1
            elif vote == "let":
                video.result.let += 1
            elif vote == "nolet":
                video.result.no_let += 1
            video.result.save()

            response = render(request, "vote/already_voted.html", context={"vote": vote, 'video': video})
            return response
    else:
        form = VoteForm()
    context = {"video": video, "already_voted": already_voted, "vote": vote, "start": start}
    return render(request, "vote/video_result.html", context=context)


def chart(request, video_id):
    video = video = get_object_or_404(
        Video.objects.select_related("result"), video_id=video_id
    )
    data = {
        "labels": ["Stroke", "Let", "No Let"],
        "data": [
            int(video.result.stroke),
            int(video.result.let),
            int(video.result.no_let),
        ],
    }
    return JsonResponse(data)


@login_required
def video_form(request):
    if request.method == "POST":
        form = VideoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = VideoForm()

    return render(request, "vote/video_form.html", {"form": form})


def about(request):
    return render(request, "vote/about.html")


def rules(request):
    return render(request, "vote/squashrules.html")