from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from challenges.utils import ChallengeType


class BaseChallengeInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey('challenges.Challenge', on_delete=models.CASCADE, null=True, blank=True)
    spot = models.ForeignKey('challenges.Spot', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def base_constraint_name(self, suffix):
        """
        Generate a unique constraint name using the app label and model name.
        """
        # this doesn't work properly
        return f"{self._meta.app_label}_{self._meta.model_name}_{suffix}"
    
    @classmethod
    def constraints(cls, suffix):
        """
        Define constraints dynamically with unique names.
        """
        return [
            models.CheckConstraint(
                check=Q(challenge__isnull=False) | Q(spot__isnull=False),
                name=cls.base_constraint_name(cls, suffix + "challenge_or_spot_not_null"),
            )
        ]

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
        """
        Create a query filter based on the challenge and its type.

        Args:
            challenge: The challenge or spot instance to query.
            challenge_type: The type of the challenge, can be either ChallengeType.CHALLENGE or ChallengeType.SPOT.

        Returns:
            A Q object representing the query filter based on the challenge type.
        """
        if challenge_type == ChallengeType.CHALLENGE:
            return Q(challenge=challenge)
        elif challenge_type == ChallengeType.SPOT:
            return Q(spot=challenge)

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
        return f"Interaction by {self.user} for {self.parent}"


class ChallengeLike(BaseChallengeInteraction):
    class Meta:
        constraints = BaseChallengeInteraction.constraints("challenge_like")

    def __str__(self):
        return f"Like by {self.user} for {self.parent}"


class ChallengeComment(BaseChallengeInteraction):
    comment = models.CharField(max_length=1000)

    class Meta:
        constraints = BaseChallengeInteraction.constraints("challenge_comment")

    def __str__(self):
        return f"Comment by {self.user} for {self.parent}"
