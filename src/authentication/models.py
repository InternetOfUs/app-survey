from __future__ import absolute_import, annotations

from django.db import models


class CachedCredentials(models.Model):

    key = models.CharField(max_length=1024)
    data = models.JSONField()
