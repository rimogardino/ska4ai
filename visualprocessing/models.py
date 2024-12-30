import subprocess
from django.db import models


class VisualsQueue(models.Model):
    visual = models.URLField()
    file_type = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the instance first
        subprocess.Popen(
                ['python3', 'manage.py', 'process_visual_queue'],
            )