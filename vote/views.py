from django.shortcuts import render, redirect
from .forms import VideoForm
from .models import Video, Result


# Create your views here.
def index(request):
    videos = Video.objects.filter(is_active=True, is_posted=True).exclude(
        comment_id__isnull=True
    )
    context = {
        "videos": videos,
    }
    return render(request, "vote/index.html", context=context)


def video_form(request):
    if request.method == "POST":
        form = VideoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = VideoForm()

    return render(request, "vote/video_form.html", {"form": form})
