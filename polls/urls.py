from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("create/", views.create_poll, name="create_poll"),
    path("poll/<slug:slug>/", views.poll_detail, name="poll_detail"),
    path("poll/<slug:slug>/stop/", views.stop_poll, name="stop_poll"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("history/", views.history, name="history"),
    path("vote/<slug:slug>/", views.vote, name="vote"),
]