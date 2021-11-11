from __future__ import absolute_import, annotations

import re

from django.utils import translation


class ActivateTranslationMixin:

    @staticmethod
    def initialize_translations(locale: str = "en"):
        if re.match(r"it", locale):
            translation.activate("it")
        elif re.match(r"es", locale):
            translation.activate("es")
        elif re.match(r"mn", locale):
            translation.activate("mn")
        elif re.match(r"da", locale):
            translation.activate("en")  # TODO add da translations ?
        else:
            translation.activate("en")
