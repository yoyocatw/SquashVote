from django.shortcuts import render, redirect, get_object_or_404
from .forms import VideoForm
from .models import Video, YoutubeQuota
from django.http import JsonResponse
from django.utils.timezone import now


# Create your views here.
def index(request):
    videos = (
        Video.objects.filter(is_active=True, is_posted=True)
        .exclude(comment_id__isnull=True)
        .select_related("result")
    )
    quota, create = YoutubeQuota.objects.get_or_create(
        date=now().date(), defaults={"quota": 0}
    )
    quota_reached = False
    if quota.quota + 50 > 10000:
        quota_reached = True
    context = {"videos": videos, "quota": quota, "quota_reached": quota_reached}
    return render(request, "vote/index.html", context=context)


def video_result(request, video_id):
    video = get_object_or_404(Video.objects.select_related("result"), video_id=video_id)
    context = {
        "video": video,
    }
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


def archived(request):
    videos = (
        Video.objects.filter(is_active=False, is_posted=True)
        .exclude(comment_id__isnull=True)
        .select_related("result")
    )
    context = {"videos": videos}
    return render(request, "vote/archived.html", context=context)


def archived_result(request, video_id):
    video = get_object_or_404(Video.objects.select_related("result"), video_id=video_id)
    context = {
        "video": video,
    }
    return render(request, "vote/archived_result.html", context=context)
