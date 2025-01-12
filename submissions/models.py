import os
from django.db import models
from django.conf import settings
from userinteraction.models import BaseChallengeInteraction


# Create your models here.
class Submission(BaseChallengeInteraction):
    visual = models.FileField(upload_to="submissions/", null=True)
    file_type = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False, blank=True, null=True)

    def approve(self):
        self.approved = True
        self.save()
        self.parent.update()

    def disapprove(self):
        self.approved = False
        self.save()
        self.parent.update()

    def reset_state(self):
        self.approved = None
        self.save()
        self.parent.update()

    @property
    def processed_url(self):
        """
        Return the URL for the processed file.
        """
        base, ext = os.path.splitext(self.visual.name)
        if self.file_type.startswith('video'):
            processed_name = f"{base}_processed.mp4"
        else:
            processed_name = f"{base}_processed.jpg"
        return f"{settings.MEDIA_URL}{processed_name}"

    class Meta:
        constraints = BaseChallengeInteraction.constraints("submission")

    def __str__(self):
        return f"Submission by {self.user} for {self.parent} with points {self.parent.points}"
