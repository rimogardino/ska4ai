from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from challenges.utils import ChallengeType


# Create your models here.
# class Like(models.Model):
#     liked_by = models.ForeignKey(User, on_delete=models.CASCADE)
#     liked_on = models.DateTimeField(auto_now_add=True)
#     # Generic foreign key to a Challenge
#     generic_object = GenericForeignKey('content_type', 'object_id')
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()


#     class Meta:
#         unique_together = ["liked_by", "object_id"]

#     def __str__(self):
#         return f"{self.liked_by} likes {self.challenge}"

class BaseChallengeInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey('challenges.Challenge', on_delete=models.CASCADE, null=True, blank=True)
    spot = models.ForeignKey('challenges.Spot', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        constraints = [
            # Database-level constraint
            models.CheckConstraint(
                check=Q(challenge__isnull=False) | Q(spot__isnull=False),
                name='challenge_or_spot_not_null'
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


class ChallengeLike(models.Model):
    liked_challenge = models.ForeignKey('challenges.Challenge', on_delete=models.CASCADE, null=True, blank=True)
    liked_spot = models.ForeignKey('challenges.Spot', on_delete=models.CASCADE, null=True, blank=True)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    liked_on = models.DateTimeField(auto_now_add=True)

    @property
    def liked_object(self):
        if self.liked_challenge:
            return self.liked_challenge
        elif self.liked_spot:
            return self.liked_spot
        raise AssertionError("Neither 'liked_challenge' nor 'liked_spot' is set")

    @liked_object.setter
    def liked_object(self, challenge):
        if ChallengeType.CHALLENGE == challenge.challenge_type:
            self.liked_challenge = challenge
        elif ChallengeType.SPOT == challenge.challenge_type:
            self.liked_spot = challenge
        else:
            raise AssertionError("Neither 'liked_challenge' nor 'liked_spot' is set")

    @classmethod
    def query_by_liked_challenge(cls, challenge, challenge_type):
        if challenge_type == ChallengeType.CHALLENGE:
            return Q(liked_challenge=challenge)
        elif challenge_type == ChallengeType.SPOT:
            return Q(liked_spot=challenge)

    class Meta:
        constraints = [
            # Database-level constraint
            models.CheckConstraint(
                check=Q(liked_challenge__isnull=False) | Q(liked_spot__isnull=False),
                name='liked_challenge_or_liked_spot_not_null'
            )
        ]
    
    def clean(self):
        # Model-level validation
        if self.liked_challenge is None and self.liked_spot is None:
            raise ValidationError(
                'At least one of liked_challenge or liked_spot must be set.'
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ChallengeComment(BaseChallengeInteraction):
    comment = models.CharField(max_length=1000)

    def __str__(self):
        return f"Comment by {self.user} for {self.parent}"
