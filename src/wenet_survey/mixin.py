from django.utils import translation


class ActivateTranslationMixin:
    def initialize_translations_request(self, request, *args, **kwargs):
        # TODO get logged user language
        translation.activate('it')
