#!/bin/bash
# Should be run when a visual is uploaded by the visualprocessing VisualsQueue save method
# We also run this from a cron job
#
# Steps for the cron job:
#
# chmod +x process_visual_queue.sh
# crontab -e
# add the following job line at the end of the file:
# */20 * * * * /bin/bash /home/webserver/ska4ai/process_visual_queue.sh >> /tmp/process_visual_queue.log 2>&1
#
# This runs the command every 20 minutes and redirects the output to a log file in tmp

# For the cronjob
# Navigate to the Django project directory
cd $1

# Activate the virtual environment if any
source $(<.project_virtual_environment.conf)

# Run the management command
python3 manage.py process_visual_queue

# Deactivate the virtual environment
deactivate