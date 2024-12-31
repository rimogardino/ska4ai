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

# Activate the virtual environment if any
project_virtual_environment=$(<.project_virtual_environment.conf)
source $(project_virtual_environment)

# Run the management command
python3 manage.py process_visual_queue

# Deactivate the virtual environment
deactivate