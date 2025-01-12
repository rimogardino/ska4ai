from django.contrib import admin
from .models import ChallengeComment, ChallengeLike, Notification
# Register your models here.
admin.site.register(ChallengeComment)
admin.site.register(ChallengeLike)
admin.site.register(Notification)
