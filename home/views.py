from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from events.models import Event
from challenges.models import Challenge, Spot, get_challenge_model_class
from challenges.serializers import geojson_serialize
from submissions.models import Submission
import json
from pathlib import Path


home = Path.home()
with open(home / ".django_envs.json", "r") as f:
    django_envs = json.load(f)[0]


# Create your views here.
def index(request):
    spots = Spot.objects.all().order_by('date')
    challenges = Challenge.objects.all().order_by('-date')
    all_challenges = [*spots, *challenges]
    [print(f"Challenge {challenge.description} has date {challenge.date}") for challenge in all_challenges]
    event_list = Event.objects.all()
    json_data = {"challenge_list": geojson_serialize(all_challenges)}
    context = {"all_challenges": all_challenges, 
               "event_list": event_list, 
               "json_data": json_data, 
               "mapbox_api_key": django_envs['MAPBOX_API_KEY']}
    return render(request, "home/index.html", context)

def leaderboard(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    leaderboard = {}
    challenge_type = event.challenge_type
    challenge_model = get_challenge_model_class(challenge_type)
    if hasattr(challenge_model, "points"):
        users = User.objects.all()
        for user in users:
            user.submission_points = (Submission.objects.filter(
                                                user=user
                                                ).aggregate(
                                                    Sum('challenge__points'))['challenge__points__sum']
                                    or 0)
            user.challenge_points = (Challenge.objects
                                                .filter(user=user)
                                                .order_by(F('points')
                                                .desc())[:event.n_challenges_for_leaderboard]
                                                .aggregate(Sum('points'))['points__sum']
                                    or 0)
            user.points = user.submission_points + user.challenge_points
            leaderboard[user.username] = user.points
            print(f"user {user.username} has challenge points {user.challenge_points} " 
                  + f"and submission points {user.submission_points} and total {user.points} points")
        leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
        print("leaderboard", leaderboard)
    context = {"event": event, "leaderboard": leaderboard}
    return render(request, "home/leaderboard.html", context)