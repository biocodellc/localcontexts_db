#!/usr/bin/env sh

#
# This script is an entry point for the App Engine Standard deployment.
#
# The script first sets up the environment variables by executing the `env.sh` script
# and then starts the gunicorn server.
#

. ./env.sh
python manage.py run_data_backup &
gunicorn -b :$PORT -w 2 --timeout 90 localcontexts.wsgi:application
