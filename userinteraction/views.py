from django.db import models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.template.loader import render_to_string
from .models import ChallengeLike, ChallengeComment, Notification, NotificationTypes
from .forms import ChallengeCommentForm
from challenges.models import get_challenge_model_class
from events.decorators import require_active_event


# Create your views here.
@login_required
@require_active_event
def like_challenge(request, challenge_id, challenge_type):
    challenge_model = get_challenge_model_class(challenge_type)
    challenge = challenge_model.objects.get(pk=challenge_id)

    liked_challenges_query = ChallengeLike.query_by_parent_challenge(challenge, challenge_type)
    current_like = ChallengeLike.objects.filter(liked_challenges_query, user=request.user)

    if current_like:
        current_like.delete()
    else:
        like = ChallengeLike(user=request.user)
        like.parent = challenge
        like.save()
    likes_count = ChallengeLike.objects.filter(liked_challenges_query).count()
    likes_points_html = _("<span>{likes_count} Likes</span>").format(likes_count=likes_count)
    if hasattr(challenge, 'points'):
        challenge.update()
        likes_points_html = _("<span>{likes_count} Likes</span> <span>{challenge_points:n} Points</span>").format(likes_count=likes_count, challenge_points=challenge.points)
    return HttpResponse(likes_points_html)


def create_comment(request, challenge_type, challenge_id):
    challenge_model = get_challenge_model_class(challenge_type)
    challenge = challenge_model.objects.get(pk=challenge_id)

    if request.method == "POST":
        form = ChallengeCommentForm(request.POST)
        form.instance.user = request.user
        form.instance.parent = challenge
        if form.is_valid():
            comment = form.save()
            if request.user != challenge.user:
                create_notification(request,
                                    NotificationTypes.NEW_COMMENT,
                                    challenge,
                                    message=comment.comment)
            html = render_to_string('userinteraction/comment.html', {'comment': comment})
            return HttpResponse(html)
    else:
        form = ChallengeCommentForm()
    context = {
        'form': form,
        'challenge': challenge
    }
    # miaybe change to HttpResponse for consistency?
    return render(request, 'userinteraction/create_comment.html', context)


def create_notification(request, notif_type, challenge, message=""):
    """
    Creates a notification for the given notification type.

    The message is a string describing the notification. Examples:

    * New comment: "{message[:30]}.. by {request.user}"
    * Your challenge {challenge_id} has been approved
    * Your challenge {challenge_id} has been disapproved
    * Your submission {submission_id} has been approved
    * Your submission {submission_id} has been disapproved

    The notif_type is one of the NotificationTypes constants.
    """
    notification = Notification(user=challenge.user)
    notification.message = message
    notification.parent = challenge.parent if hasattr(challenge, 'parent') else challenge
    notification.parent_id = challenge.id
    notification.notif_type = notif_type
    notification.save()


def get_all_comments(request, challenge_type, challenge_id):
    challenge_model = get_challenge_model_class(challenge_type)
    challenge = challenge_model.objects.get(pk=challenge_id)
    challenge_comments_query = ChallengeComment.query_by_parent_challenge(challenge, challenge_type)
    comments = ChallengeComment.objects.filter(challenge_comments_query).order_by('-created_at')
    form = ChallengeCommentForm()
    context = {
        'comments': comments,
        'challenge': challenge,
        'form': form,
    }
    return render(request, 'userinteraction/get_all_comments.html', context)


def get_notifications(request):
    notifications = None
    read_notifications = None
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, viewed=False).order_by('-created_at')
        read_notifications = Notification.objects.filter(user=request.user, viewed=True).order_by('-created_at')[:5]
    context = {
        'notifications': notifications,
        'read_notifications': read_notifications,
    }
    print("get_notifications context", context)
    html = render(request, 'userinteraction/notifications.html', context)
    return HttpResponse(html)


def get_notiications_count(request):
    count = Notification.objects.filter(user=request.user, viewed=False).count()
    return HttpResponse(count)


def read_notification(request, notification_id):
    notification = Notification.objects.get(pk=notification_id)
    notification.mark_viewed()
    return HttpResponse(_("Notification read"))
