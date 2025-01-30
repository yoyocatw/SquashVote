from django.shortcuts import render, redirect, get_object_or_404 
from .forms import VideoForm
from .models import Video, Result
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import StringIO
import matplotlib.ticker as ticker
from django.http import JsonResponse



# Create your views here.
def index(request):
    videos = Video.objects.filter(is_active=True, is_posted=True).exclude(
        comment_id__isnull=True
    ).select_related("result")
    context = {
        "videos": videos,
    }
    return render(request, "vote/index.html", context=context)

def video_result(request, video_id):
    video = get_object_or_404(Video.objects.select_related("result"), video_id=video_id)
    context = {
        "video": video,
    }
    return render(request, "vote/video_result.html", context=context)

def chart(request, video_id):
    video = video = get_object_or_404(Video.objects.select_related("result"), video_id=video_id) 
    data = {
        "labels": ["Stroke", "Let", "No Let"],
        "data": [int(video.result.stroke), int(video.result.let), int(video.result.no_let)],
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
