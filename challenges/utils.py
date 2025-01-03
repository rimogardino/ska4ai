from django.db import models
from django.utils.translation import gettext_lazy as _

class ChallengeType(models.TextChoices):
    CHALLENGE = "CH", _("Challenge")
    SPOT = "SP", _("Spot")