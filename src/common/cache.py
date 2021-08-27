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
            older_credentials = CachedCredentials.objects.get(
                key=key,
            )
            with transaction.atomic():
                older_credentials.delete()
        except CachedCredentials.DoesNotExist:
            pass

        cached_credentials = CachedCredentials(key=key, data=data)
        with transaction.atomic():
            cached_credentials.save()
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
        with transaction.atomic():
            try:
                older_credentials = CachedCredentials.objects.get(
                    key=updated_key,
                )
                with transaction.atomic():
                    older_credentials.delete()
            except CachedCredentials.DoesNotExist:
                pass
            cached_credentials.key = updated_key
            cached_credentials.save()
        return cached_credentials.key
