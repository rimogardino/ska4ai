from django.db import models

class ChallengeType(models.TextChoices):
    CHALLENGE = "CH", "Challenge"
    SPOT = "SP", "Spot"