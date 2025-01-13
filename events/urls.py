from django.urls import path
from . import views

urlpatterns = [
    path("event_info/<int:event_id>/", views.event_info, name="event_info"),
]