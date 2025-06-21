import os
from math import ceil
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from .utils import ChallengeType
from events.models import Event
from submissions.models import Submission
from userinteraction.models import ChallengeLike, BaseChallengeInteraction


def get_challenge_model_class(challenge_type):
    if challenge_type == Challenge.challenge_type:
        return Challenge
    elif challenge_type == Spot.challenge_type:
        return Spot
    else:
        raise AssertionError(
            "Provided challenge_type doesn't match any existing challenge type"
        )


# Create your models here.
class BaseChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, verbose_name="Event", on_delete=models.CASCADE)
    description = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=None, blank=True, null=True)

    def approve(self):
        self.approved = True
        self.save()

    def disapprove(self):
        self.approved = False
        self.save()

    def reset_state(self):
        self.approved = None
        self.save()

    class Meta:
        abstract = True


class Visual(BaseChallengeInteraction):
    file = models.FileField(upload_to="challenge_visuals/", null=True)
    file_type = models.CharField(max_length=50)

    @property
    def processed_url(self):
        """
        Return the URL for the processed file.
        """
        base, ext = os.path.splitext(self.file.name)
        if self.file_type.startswith("video"):
            processed_name = f"{base}_processed.mp4"
        else:
            processed_name = f"{base}_processed.jpg"
        return f"{settings.MEDIA_URL}{processed_name}"

    def __str__(self):
        return f"Visual--for {self.parent}"


class MapPoint(models.Model):
    # Latitude is north-south and longitude is east-west,
    # so latitude is analogous to Y (up-down) and
    # longitude is analogous to X (right-left).
    # Latitude is between -90 and 90, longitude is between -180 and 180.
    # https://en.wikipedia.org/wiki/Geographic_coordinate_system
    # longitude is X, latitude is Y
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)

    class Meta:
        abstract = True


class Spot(BaseChallenge, MapPoint):
    name = models.CharField(max_length=50)
    challenge_type = ChallengeType.SPOT

    def __str__(self):
        return f"{self.name}--{self.event}-{self.pk}-: {self.description}"


class Challenge(BaseChallenge, MapPoint):
    points = models.IntegerField(default=1)
    challenge_type = ChallengeType.CHALLENGE

    def update(self):
        """
        Updates the state of a challenge.

        Args:
            add_likes (int): The number of likes to add to the challenge
            add_completions (int): The number of completions to add to the challenge

        Returns:
            None
        """
        likes = ChallengeLike.objects.filter(challenge=self).count() + 1
        n_completions = Submission.objects.filter(challenge=self, approved=True).count()
        if n_completions == 0:
            n_completions = 1
        self.points = ceil(likes / n_completions)
        # Save the updated challenge
        self.save()

    def __str__(self):
        return f"{self.event.name}-{self.user}-id:{self.pk}-points: {self.points}-: {self.description}"
