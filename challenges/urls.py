from django.urls import path
from . import views

app_name = 'challenges'

urlpatterns = [
    path('create_challenge/<int:event_id>/', views.create_challenge, name='create_challenge'),
    path('edit_challenge/<str:challenge_type>/<int:challenge_id>/', views.edit_challenge, name='edit_challenge'),
    path('delete_challenge/<str:challenge_type>/<int:challenge_id>/', views.delete_challenge, name='delete_challenge'),
    path('<str:challenge_type>/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path("<str:challenge_type>/<int:challenge_id>/simple_info", views.challenge_simple_info, name="challenge_simple_info"),
]