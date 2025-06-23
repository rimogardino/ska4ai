from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("leaderboard/<int:event_id>/", views.leaderboard, name="leaderboard"),
    path("about", views.about, name="about"),
]