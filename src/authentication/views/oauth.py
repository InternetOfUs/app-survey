from __future__ import absolute_import, annotations

import logging
import uuid

from django.conf import settings
from django.shortcuts import redirect, render
from rest_framework.request import Request
from rest_framework.views import APIView
from wenet.interface.client import Oauth2Client

from common.cache import DjangoCache


logger = logging.getLogger("wenet-survey-web-app.authentication.views.oauth")


class OauthView(APIView):

    def get(self, request: Request):
        if not request.session.get("has_logged", False):
            try:
                oauth2_code = request.query_params.get("code", None)
                resource_id = str(uuid.uuid4())
                cache = DjangoCache()
                Oauth2Client.initialize_with_code(
                    settings.WENET_APP_ID,
                    settings.WENET_APP_SECRET,
                    oauth2_code,
                    settings.OAUTH_CALLBACK_URL,
                    resource_id,
                    cache,
                    token_endpoint_url=f"{settings.WENET_INSTANCE_URL}/api/oauth2/token"
                )
                request.session["has_logged"] = True
                request.session["resource_id"] = resource_id
                request.session["cache"] = cache.to_repr()
                return redirect(f"/{settings.BASE_URL}")
            except Exception as e:
                logger.exception("Something went wrong during the login operation", exc_info=e)
                context = {
                    "error_title": "Error during login",
                    "error_message": f"There was an error during the login, please try again ",
                    "add_link": True,
                    "link_url": f"{settings.WENET_INSTANCE_URL}/hub/frontend/oauth/login?client_id={settings.WENET_APP_ID}",
                    "link_text": "here"
                }
                return render(request, "authentication/error.html", context=context)
        else:
            return redirect(f"/{settings.BASE_URL}")
