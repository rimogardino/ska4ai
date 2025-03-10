from django.urls import path
from . import views

app_name = 'userinteraction'

urlpatterns = [
    # path('like_object/<int:object_id>/', views.like_object, name='like_object'),
    path('like_challenge/<int:challenge_id>/<str:challenge_type>/', views.like_challenge, name='like_challenge'),
    path("create_comment/<str:challenge_type>/<int:challenge_id>/", views.create_comment, name="create_comment"),
    path("get_all_comments/<str:challenge_type>/<int:challenge_id>/", views.get_all_comments, name="get_all_comments"),
    # Notifications
    path("get_notifications/", views.get_notifications, name="get_notifications"),
    path("get_notiications_count/", views.get_notiications_count, name="get_notiications_count"),
    path("read_notification/<int:notification_id>/", views.read_notification, name="read_notification"),
]