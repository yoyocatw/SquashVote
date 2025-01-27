from django.shortcuts import render, redirect, get_object_or_404
from .forms import VideoForm
from .models import Video, Result
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import StringIO


# Create your views here.
def index(request):
    videos = Video.objects.filter(is_active=True, is_posted=True).exclude(
        comment_id__isnull=True
    ).select_related("result")
    context = {
        "videos": videos,
    }
    return render(request, "vote/index.html", context=context)

def video_result(request, video_title):
    video = get_object_or_404(Video.objects.select_related("result"), video_title=video_title)
    stroke_percentage = (video.result.stroke / video.result.total_votes) * 100
    let_percentage = (video.result.let / video.result.total_votes) * 100
    no_let_percentage = (video.result.no_let / video.result.total_votes) * 100
    percentages = {
            "stroke": stroke_percentage,
            "let": let_percentage,
            "no_let": no_let_percentage,
    }
    choices = ['Stroke', 'Let', 'No Let']
    percentages = [percentages['stroke'], percentages['let'], percentages['no_let']]
    colour_map = {'Stroke': '#EC6B56', 'Let': '#FFC154', 'No Let': '#6CA0DC'}
    results = {choices[i]: percentages[i] for i in range(len(choices)) if percentages[i] > 0}
    labels = list(results.keys())
    percent = list(results.values())
    colours = [colour_map[label] for label in labels]

    fig, ax = plt.subplots()
    chart = ax.pie(percent, labels=labels, autopct='%1.0f%%', colors=colours, startangle=90, pctdistance=0.6, radius=0.8)
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    graph = imgdata.getvalue() 
    context = {
        "video": video,
        "chart": graph,
    }
    return render(request, "vote/video_result.html", context=context)

def video_form(request):
    if request.method == "POST":
        form = VideoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = VideoForm()

    return render(request, "vote/video_form.html", {"form": form})
