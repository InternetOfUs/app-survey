from __future__ import absolute_import, annotations

import logging

from wenet.storage.cache import InMemoryCache


logger = logging.getLogger("wenet-survey-web-app.ws.common.cache")


class DjangoCache(InMemoryCache):

    def to_repr(self) -> dict:
        return self._cache

    @staticmethod
    def from_repr(raw_cache: dict) -> DjangoCache:
        django_cache = DjangoCache()
        django_cache._cache = raw_cache
        return django_cache
