from __future__ import absolute_import, annotations

import logging

from django.conf import settings
from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.views import APIView
from wenet.interface.client import Oauth2Client
from wenet.interface.exceptions import RefreshTokenExpiredError
from wenet.interface.service_api import ServiceApiInterface

from common.cache import DjangoCacheCredentials


logger = logging.getLogger("wenet-survey-web-app.authentication.views.home")


class HomeView(APIView):

    def get(self, request: Request):
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
                    "user_first_name": user_profile.name.first,
                    "logout_link": f"/{settings.BASE_URL}logout/",
                    "survey_link": f"/{settings.BASE_URL}survey/"
                }
                return render(request, "authentication/home_logged.html", context=context)
            except RefreshTokenExpiredError:
                logger.info("Token expired")
                request.session["has_logged"] = False
                request.session["resource_id"] = None
                context = {
                    "error_title": "Session expired",
                    "error_message": f"Your session is expired, log ",
                    "add_link": True,
                    "link_url": f"{settings.WENET_INSTANCE_URL}/hub/frontend/oauth/login?client_id={settings.WENET_APP_ID}",
                    "link_text": "here"
                }
                return render(request, "error.html", context=context)
            except Exception as e:
                logger.exception("Unexpected error occurs", exc_info=e)
                request.session["has_logged"] = False
                request.session["resource_id"] = None
                context = {
                    "error_title": "Unexpected error",
                    "error_message": f"An unexpected error occurs, log again ",  # TODO check this message
                    "add_link": True,
                    "link_url": f"{settings.WENET_INSTANCE_URL}/hub/frontend/oauth/login?client_id={settings.WENET_APP_ID}",
                    "link_text": "here"
                }
                return render(request, "error.html", context=context)
        else:
            context = {
                "login_url": f"{settings.WENET_INSTANCE_URL}/hub/frontend/oauth/login?client_id={settings.WENET_APP_ID}"
            }
            return render(request, "authentication/home_not_logged.html", context=context)
