from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from .models import ChallengeLike, ChallengeComment
from .forms import ChallengeCommentForm
from challenges.models import get_challenge_model_class

# Create your views here.
@login_required
def like_challenge(request, challenge_id, challenge_type):
    challenge_model = get_challenge_model_class(challenge_type)
    challenge = challenge_model.objects.get(pk=challenge_id)

    liked_challenges_query = ChallengeLike.query_by_liked_challenge(challenge, challenge_type)
    current_like = ChallengeLike.objects.filter(liked_challenges_query, liked_by=request.user)

    if current_like:
        current_like.delete()
    else:
        like = ChallengeLike(liked_by=request.user)
        like.liked_object = challenge
        like.save()
    try:
        challenge.update()
    except AttributeError as e:
        print(e)
    likes_count = ChallengeLike.objects.filter(liked_challenges_query).count()

    likes_points_html = f"<span>{likes_count} Likes</span> <span>{challenge.points:n} Points</span>" if challenge.points else f"<span>{likes_count} Likes</span>"
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

def get_all_comments(request, challenge_type, challenge_id):
    challenge_model = get_challenge_model_class(challenge_type)
    challenge = challenge_model.objects.get(pk=challenge_id)
    challenge_comments_query = ChallengeComment.query_by_parent_challenge(challenge, challenge_type)
    comments = ChallengeComment.objects.filter(challenge_comments_query)
    form = ChallengeCommentForm()
    context = {
        'comments': comments,
        'challenge': challenge,
        'form': form,
    }
    return render(request, 'userinteraction/get_all_comments.html', context)