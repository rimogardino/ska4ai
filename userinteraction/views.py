from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from .models import ChallengeLike, ChallengeComment, Notification
from .forms import ChallengeCommentForm
from challenges.models import get_challenge_model_class
from events.decorators import require_active_event
from events.models import States


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
    likes_points_html = f"<span>{likes_count} Likes</span>"
    if hasattr(challenge, 'points'):
        challenge.update()
        likes_points_html = f"<span>{likes_count} Likes</span> <span>{challenge.points:n} Points</span>"
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
                _create_notification(request, challenge, message=comment.comment)
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

def _create_notification(request, challenge, message):
    notification = Notification(user=challenge.user)
    notification.save()
    notification_context = {"challenge": challenge, "notification_id": notification.pk, "message": f"\"{message[:30]}..\" by {request.user}"}
    template = 'userinteraction/notification_messages/created_comment.html'
    notification.message = render_to_string(
                                            template,
                                            notification_context)
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
    html = render(request, 'userinteraction/notifications.html', context)
    return HttpResponse(html)

def get_notiications_count(request):
    count = Notification.objects.filter(user=request.user, viewed=False).count()
    return HttpResponse(count)

def read_notification(request, notification_id):
    notification = Notification.objects.get(pk=notification_id)
    notification.mark_viewed()
    return HttpResponse("Notification read")
