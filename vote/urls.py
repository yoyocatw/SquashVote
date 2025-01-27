from django.urls import path
from .views import video_form, index, video_result

urlpatterns = [
    path("", index, name="index"),
    path("video/<str:video_title>/",video_result, name="video_result"),
    path("videoform/", video_form, name="video_form"),
]
