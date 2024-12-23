from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from challenges.utils import ChallengeType


# Create your models here.
class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    visual = models.FileField(upload_to="submissions/", null=True)
    approved = models.BooleanField(default=False)
    # Foreign keys to a Challenge
    challenge = models.ForeignKey('challenges.Challenge', on_delete=models.CASCADE, null=True, blank=True)
    # Why do I have this???
    spot = models.ForeignKey('challenges.Spot', on_delete=models.CASCADE, null=True, blank=True)

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
                name='submission_challenge_or_spot_not_null'
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
        return f"Submission by {self.user} for {self.parent} with points {self.parent.points}"
