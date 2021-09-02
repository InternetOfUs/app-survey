from __future__ import absolute_import, annotations

from django.db import models


class FailedProfileUpdateTask(models.Model):

    failure_datetime = models.DateTimeField()
    wenet_id = models.CharField(max_length=1024)
    raw_survey_answer = models.JSONField()

    class Meta:

        verbose_name = "Failed profile update task"
        verbose_name_plural = "Failed profile update tasks"


class LastUserProfileUpdate(models.Model):

    last_update = models.DateTimeField()
    wenet_id = models.CharField(max_length=1024)

    class Meta:

        verbose_name = "Last user profile update"
        verbose_name_plural = "Last user profile updates"
