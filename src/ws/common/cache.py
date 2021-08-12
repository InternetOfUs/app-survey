from __future__ import absolute_import, annotations

import logging

from wenet.storage.cache import InMemoryCache


logger = logging.getLogger("wenet-survey-web-app.ws.common.cache")


cache = InMemoryCache()
