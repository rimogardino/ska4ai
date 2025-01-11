from django.urls import path
from . import views

app_name = 'submissions'

urlpatterns = [
    path("create_submission/<str:challenge_type>/<int:challenge_id>/", views.create_submission, name="create_submission"),
    path("submission_detail/<int:submission_id>/", views.submission_detail, name="submission_detail"),
    path("submission_moderation/<int:submission_id>/", views.submission_moderation, name="submission_moderation"),
    path("<int:submission_id>/approve_submission", views.approve_submission, name="approve_submission"),
    path("<int:submission_id>/disapprove_submission", views.disapprove_submission, name="disapprove_submission"),
    path("<int:submission_id>/reset_submission_state", views.reset_submission_state, name="reset_submission_state"),
    path("edit_submission/<int:submission_id>/", views.edit_submission, name="edit_submission"),
    path("delete_submission/<int:submission_id>/", views.delete_submission, name="delete_submission"),
]