import subprocess
from django.db import models


class VisualsQueue(models.Model):
    """
    A queue of visuals to be processed.

    The processing happens by calling:
    python3 manage.py process_visual_queue

    which is handled by the process_visual_queue.sh 
    script called by a cron job every so often.
    """
    visual = models.URLField()
    file_type = models.CharField(max_length=50)
