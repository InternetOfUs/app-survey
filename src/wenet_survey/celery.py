from __future__ import absolute_import, annotations

import os

from celery import Celery

# set the default Django settings module for the "celery" program.
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wenet_survey.settings")

app = Celery("wenet_survey")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace="CELERY" means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

default_schedule = {
    "recover_profile_update_errors": {
        "task": "tasks.tasks.recover_profile_update_errors",
        "schedule": crontab(minute="*/15"),  # Execute every 15 minutes
        "args": (),
    }
}

app.conf.beat_schedule = default_schedule
