from django.urls import path
from .views import video_form, index, video_result, chart, about, archived, archived_result
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", index, name="index"),
    path("video/<str:video_id>/",video_result, name="video_result"),
    path("videoform/", login_required(video_form), name="video_form"),
    path("chart/<str:video_id>/", chart, name="chart"),
    path("about/", about, name="about"),
    path("archived/", archived, name="archived"),
    path("archived/<str:video_id>/",archived_result, name="archived_result"),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]