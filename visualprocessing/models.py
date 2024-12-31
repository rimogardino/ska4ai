import subprocess
import os
from django.db import models
from django.conf import settings


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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        os.chdir(settings.BASE_DIR)
        # Try except for when running on windows for dev purposes
        try:
            with open('/tmp/process_visual_queue_model.log', 'a') as log_file:
                subprocess.Popen(
                        ['/bin/bash', 'process_visual_queue.sh', settings.BASE_DIR],
                        stdout=log_file,
                        stderr=log_file,
                    )
        except FileNotFoundError as e:
            print(e)
            print("process_visual_queue.sh not found, probably because we are on windows")
            print("Run the script manually or wait for the cron job to run it")
            