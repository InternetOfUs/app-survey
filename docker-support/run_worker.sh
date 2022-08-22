#!/bin/bash


echo "Running worker..."

#
# Important note: env variables should not be passed as arguments to the module!
# This will allow for an easier automatisation of the docker support creation.
#




exec celery -A wenet_survey worker -B -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

