from django.http import HttpResponse
from django.shortcuts import render
from .models import ChallengeLike
from challenges.models import get_challenge_model_class
from challenges.utils import ChallengeType

# Create your views here.
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
    return HttpResponse(likes_count)
