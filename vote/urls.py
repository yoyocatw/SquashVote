from django.urls import path
from .views import (
    video_form,
    index,
    video_result,
    chart,
    about,
    rules,
    post_comment,
    like_comment,
    post_reply,
    report_comment,
    confirm,
    review,
    accept_video,
    reject_video,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", index, name="index"),
    path(
        "video/<int:video_id>/accept/", accept_video, name="accept_video"
    ),  # Has to be before video_result or it will match wrong.
    path("video/<int:video_id>/reject/", reject_video, name="reject_video"),
    path("video/<int:pk>/<slug:slug>/", video_result, name="video_result"),
    path("videoform/", video_form, name="video_form"),
    path("chart/<str:video_id>/", chart, name="chart"),
    path("about/", about, name="about"),
    path("rules/", rules, name="rules"),
    path("post_comment/<str:video_id>/", post_comment, name="post_comment"),
    path("comment/<int:comment_id>/like_comment", like_comment, name="like_comment"),
    path("comment/<int:comment_id>/reply/", post_reply, name="post_reply"),
    path("report_comment/<int:comment_id>/", report_comment, name="report"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("confirm/", confirm, name="confirm"),
    path("review/", review, name="review"),
]
