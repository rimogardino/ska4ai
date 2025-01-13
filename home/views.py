from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from events.models import Event, States
from challenges.models import Challenge, Spot, get_challenge_model_class
from challenges.serializers import geojson_serialize
from submissions.models import Submission
from userinteraction.views import get_notifications, get_notiications_count
import json
from pathlib import Path


home = Path.home()
with open(home / ".django_envs.json", "r") as f:
    django_envs = json.load(f)[0]


# Create your views here.
def index(request):
    is_moderator = request.user.groups.filter(name='Moderators').exists()
    spots = Spot.objects.filter(approved=True).order_by('-date')
    challenges = Challenge.objects.filter(approved=True).order_by('-date')
    all_challenges = [*spots, *challenges]
    active_event_list = Event.objects.filter(state=States.ACTIVE).order_by('-priority')
    archived_events = Event.objects.filter(state=States.CLOSED).order_by('-priority')
    event_list = [*active_event_list, *archived_events]
    if is_moderator:
        # User is a moderator
        spots_to_moderate = Spot.objects.filter(approved=None).exclude(user=request.user).exclude(event__state=States.CLOSED).order_by('-date')
        challenges_to_moderate = Challenge.objects.filter(approved=None).exclude(user=request.user).exclude(event__state=States.CLOSED).order_by('-date')
        submissions_to_moderate = Submission.objects.filter(approved=None).exclude(user=request.user).exclude(challenge__event__state=States.CLOSED).order_by('-date')
        for submission in submissions_to_moderate:
            submission.type = "submission"
            submission.event = submission.parent.event
        all_challenges_to_moderate = [*spots_to_moderate, *challenges_to_moderate]
        for challenge in all_challenges_to_moderate:
            challenge.type = "challenge"
        moderation_list = [*spots_to_moderate, *challenges_to_moderate, *submissions_to_moderate]
    else:
        submissions_to_moderate = None
        all_challenges_to_moderate = None
        moderation_list = []
    json_data = {"challenge_list": geojson_serialize(all_challenges)}
    context = {"all_challenges": all_challenges,
               "all_challenges_to_moderate": all_challenges_to_moderate,
               "submissions_to_moderate": submissions_to_moderate,
               "moderation_list": moderation_list,
               "active_event_list": active_event_list,
               "archived_events": archived_events,
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
            # This should probably not happen here, but be an attribute in the model and reduce the calculations
            user.submission_points = (Submission.objects.filter(
                                                user=user,
                                                approved=True
                                                ).aggregate(
                                                    Sum('challenge__points'))['challenge__points__sum']
                                    or 0)
            user.challenge_points = (Challenge.objects
                                                .filter(user=user, approved=True)
                                                .order_by(F('points')
                                                .desc())[:event.n_challenges_for_leaderboard]
                                                .aggregate(Sum('points'))['points__sum']
                                    or 0)
            user.points = user.submission_points + user.challenge_points
            if user.points > 0:
                leaderboard[user.username] = [user.points, 1]
            # print(f"user {user.username} has challenge points {user.challenge_points} " 
            #       + f"and submission points {user.submission_points} and total {user.points} points")
        leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
        # Add placings to the leaderboard
        for i, p in enumerate(leaderboard[1:]):
            prev_place = leaderboard[i][1]
            if p[1][0] == prev_place[0]:
                p[1][1] = prev_place[1]
            else:
                p[1][1] = prev_place[1] + 1
    context = {"event": event, "leaderboard": leaderboard}
    return render(request, "home/leaderboard.html", context)
