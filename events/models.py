from django.db import models
from django.utils.translation import gettext_lazy as _
from challenges.utils import ChallengeType

class States(models.TextChoices):
    HIDDEN = "HI", _("Hidden")
    ACTIVE = "AC", _("Active")
    CLOSED = "CL", _("Closed")


class Sport(models.TextChoices):
    PARKOUR = "PK", _("Parkour")


class MapRegion(models.TextChoices):
    # center: [23.321869, 42.697085] is for Sofia
    # maxBounds: [23.2, 42.6, 23.45, 42.75] is for Sofia
    SOFIA = "SO", _("Sofia")
    PLOVDIV = "PL", _("Plovdiv")
    BULGARIA = "BG", _("Bulgaria")


# https://labs.mapbox.com/location-helper
REGIONS = {
    MapRegion.SOFIA: {"center": [23.321869, 42.697085], "maxBounds": [23.2, 42.6, 23.45, 42.75], "zoom": 12},
    MapRegion.PLOVDIV: {"center": [24.75462, 42.14143], "maxBounds": [24.67489, 42.09334,24.82522, 42.18172], "zoom": 12},
    MapRegion.BULGARIA: {"center": [25.70176, 43.04402], "maxBounds": [22.20937, 41.20113,28.68793, 44.33287], "zoom": 7.5},}


# Events will be handled in the admin only
class Event(models.Model):
    name = models.CharField(default="Event", max_length=50)
    description = models.TextField(null=True, blank=True)
    short_description = models.TextField(max_length=100, null=True, blank=True)
    rules = models.TextField(null=True, blank=True)
    sport = models.CharField(choices=Sport.choices, default=Sport.PARKOUR, max_length=2)
    state = models.CharField(choices=States.choices, default=States.HIDDEN, max_length=2)
    challenge_type = models.CharField(choices=ChallengeType.choices, default=ChallengeType.CHALLENGE, max_length=2)
    # The number of challenges that add up to the score for the leaderboard
    # User can upload any nubmer of challenges, but only the top n_challenges_for_leaderboard
    # will be counted to their score.
    n_challenges_for_leaderboard = models.IntegerField(default=5)
    map_region = models.CharField(choices=MapRegion.choices, default=MapRegion.SOFIA, max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(default=0)
    
    def __str__(self):
        return " : ".join([self.name, self.short_description])

    class Meta:
        app_label  = 'events'
