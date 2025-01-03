import os
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.db.models import Q
from .utils import ChallengeType
from events.models import Event
from userinteraction.models import ChallengeLike


def get_challenge_model_class(challenge_type):
    if challenge_type == Challenge.challenge_type:
        return Challenge
    elif challenge_type == Spot.challenge_type:
        return Spot
    else:
        raise AssertionError("Provided challenge_type doesn't match any existing challenge type")


# Create your models here.
class BaseChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, verbose_name="Event", on_delete=models.CASCADE)
    description = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    disapproved = models.BooleanField(default=False)
    
    class Meta:
        abstract = True


class Visual(models.Model):
    file = models.FileField(upload_to="challenge_visuals/", null=True)
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Foreign keys to a Challenge
    challenge = models.ForeignKey('challenges.Challenge', on_delete=models.CASCADE, null=True, blank=True)
    spot = models.ForeignKey('challenges.Spot', on_delete=models.CASCADE, null=True, blank=True)

    @property
    def processed_url(self):
        """
        Return the URL for the processed file.
        """
        base, ext = os.path.splitext(self.file.name)
        if self.file_type.startswith('video'):
            processed_name = f"{base}_processed.mp4"
        else:
            processed_name = f"{base}_processed.jpg"
        return f"{settings.MEDIA_URL}{processed_name}"

    @property
    def parent(self):
        if self.challenge:
            return self.challenge
        elif self.spot:
            return self.spot
        raise AssertionError("Neither 'challenge' nor 'spot' is set")

    @parent.setter
    def parent(self, challenge):
        if ChallengeType.CHALLENGE == challenge.challenge_type:
            self.challenge = challenge
        elif ChallengeType.SPOT == challenge.challenge_type:
            self.spot = challenge
        else:
            raise AssertionError("Neither 'challenge' nor 'spot' is set")

    @classmethod
    def query_by_parent_challenge(cls, challenge, challenge_type):
        if challenge_type == ChallengeType.CHALLENGE:
            return Q(challenge=challenge)
        elif challenge_type == ChallengeType.SPOT:
            return Q(spot=challenge)

    class Meta:
        constraints = [
            # Database-level constraint
            models.CheckConstraint(
                check=Q(challenge__isnull=False) | Q(spot__isnull=False),
                name='visual_challenge_or_spot_not_null'
            )
        ]
    
    def clean(self):
        # Model-level validation
        if self.challenge is None and self.spot is None:
            raise ValidationError(
                'At least one of challenge or spot must be set.'
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

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
    name = models.CharField(default="Spot name", max_length=50)
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
        #n_completions = Submission.objects.filter(generic_challenge=self, approved=True).count()
        n_completions = 1
        if n_completions == 0:
            n_completions = 1
        self.points = likes / n_completions
        print(f"Likes: {likes}; Completions: {n_completions}; Points: {self.points}")
        # Save the updated challenge
        self.save()

    def __str__(self):
        return f'{self.event.name}-{self.user}-id:{self.pk}-points: {self.points}-: {self.description}'

