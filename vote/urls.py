from django.urls import path
from .views import video_form, index, video_result, chart, about, archived, archived_result

urlpatterns = [
    path("", index, name="index"),
    path("video/<str:video_id>/",video_result, name="video_result"),
    path("videoform/", video_form, name="video_form"),
    path("chart/<str:video_id>/", chart, name="chart"),
    path("about/", about, name="about"),
    path("archived/", archived, name="archived"),
    path("archived/<str:video_id>/",archived_result, name="archived_result"),
]
