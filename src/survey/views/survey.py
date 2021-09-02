from __future__ import absolute_import, annotations

import logging

from django.conf import settings
from django.shortcuts import redirect, render
from django.utils import translation
from rest_framework.request import Request
from rest_framework.views import APIView
from wenet.interface.client import Oauth2Client
from wenet.interface.exceptions import RefreshTokenExpiredError
from wenet.interface.service_api import ServiceApiInterface

from common.cache import DjangoCacheCredentials
from wenet_survey.mixin import ActivateTranslationMixin

logger = logging.getLogger("wenet-survey-web-app.survey.views.survey")


class SurveyView(ActivateTranslationMixin, APIView):

    def get(self, request: Request):
        super().initialize_translations_request(request)

        if request.session.get("has_logged", False):
            client = Oauth2Client(
                settings.WENET_APP_ID,
                settings.WENET_APP_SECRET,
                request.session["resource_id"],
                DjangoCacheCredentials(),
                token_endpoint_url=f"{settings.WENET_INSTANCE_URL}/api/oauth2/token"
            )
            service_api_interface = ServiceApiInterface(client, platform_url=settings.WENET_INSTANCE_URL)
            try:
                token_details = service_api_interface.get_token_details()
                user_profile = service_api_interface.get_user_profile(token_details.profile_id)
                context = {
                    "wenet_id": user_profile.profile_id,
                    "form_id": settings.SURVEY_FORM_ID  # TODO to be set accordingly to the language of the user profile
                }
                return render(request, "survey/survey.html", context=context)
            except RefreshTokenExpiredError:
                logger.info("Token expired")
                request.session["has_logged"] = False
                request.session["resource_id"] = None
                context = {
                    "error_title": translation.gettext("Session expired"),
                    "error_message": translation.gettext("Your session is expired, please login again."),
                    "add_link": True,
                    "link_url": f"{settings.WENET_INSTANCE_URL}/hub/frontend/oauth/login?client_id={settings.WENET_APP_ID}",
                    "link_text": translation.gettext("Login")
                }
                return render(request, "error.html", context=context)
            except Exception as e:
                logger.exception("Unexpected error occurs", exc_info=e)
                request.session["has_logged"] = False
                request.session["resource_id"] = None
                context = {
                    "error_title": translation.gettext("Unexpected error"),
                    "error_message": translation.gettext("An unexpected error occurs, login again."),
                    "add_link": True,
                    "link_url": f"{settings.WENET_INSTANCE_URL}/hub/frontend/oauth/login?client_id={settings.WENET_APP_ID}",
                    "link_text": translation.gettext("Login")
                }
                return render(request, "error.html", context=context)
        else:
            return redirect(f"/{settings.BASE_URL}")
