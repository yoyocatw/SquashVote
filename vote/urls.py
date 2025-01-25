from django.urls import path
from .views import video_form, index

urlpatterns = [
    path("", index, name="index"),
    path("videoform/", video_form, name="video_form"),
]
