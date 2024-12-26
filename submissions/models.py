from django.db import models
from userinteraction.models import BaseChallengeInteraction


# Create your models here.
class Submission(BaseChallengeInteraction):
    visual = models.FileField(upload_to="submissions/", null=True)
    approved = models.BooleanField(default=False)

    class Meta:
        constraints = BaseChallengeInteraction.constraints("submission")

    def __str__(self):
        return f"Submission by {self.user} for {self.parent} with points {self.parent.points}"
