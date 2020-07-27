#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.
createdb heliosdap
python manage.py syncdb
python manage.py migrate
