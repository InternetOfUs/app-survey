from __future__ import absolute_import, annotations

import logging
from typing import Optional

from django.db import transaction
from wenet.storage.cache import BaseCache

from authentication.models import CachedCredentials


logger = logging.getLogger("wenet-survey-web-app.ws.common.cache")


class DjangoCacheCredentials(BaseCache):

    def cache(self, data: dict, key: Optional[str] = None, **kwargs) -> str:
        if key is None:
            key = self._generate_id()

        try:
            credentials = CachedCredentials.objects.get(
                key=key,
            )
            credentials.data = data
        except CachedCredentials.DoesNotExist:
            credentials = CachedCredentials(key=key, data=data)

        with transaction.atomic():
            credentials.save()
        return key

    def get(self, key: str) -> Optional[dict]:
        try:
            cached_credentials = CachedCredentials.objects.get(
                key=key,
            )
            return cached_credentials.data
        except CachedCredentials.DoesNotExist:
            return None

    def update_key(self, previous_key: str, updated_key: str) -> str:
        cached_credentials = CachedCredentials.objects.get(
            key=previous_key,
        )
        try:
            user_credentials = CachedCredentials.objects.get(
                key=updated_key,
            )
        except CachedCredentials.DoesNotExist:
            user_credentials = None

        with transaction.atomic():
            if user_credentials is not None:
                user_credentials.data = cached_credentials.data
                user_credentials.save()
                cached_credentials.delete()
            else:
                cached_credentials.key = updated_key
                cached_credentials.save()
        return cached_credentials.key
