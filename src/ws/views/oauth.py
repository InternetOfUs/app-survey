from __future__ import absolute_import, annotations

import logging
import uuid

from django.http import HttpResponse, HttpResponseServerError
from rest_framework.request import Request
from rest_framework.views import APIView
from wenet.interface.client import Oauth2Client
from wenet.interface.service_api import ServiceApiInterface

from ws.common.cache import cache


logger = logging.getLogger("wenet-survey-web-app.ws.views.oauth")


class OauthView(APIView):

    def get(self, request: Request):
        try:
            oauth2_code = request.query_params.get("code", None)
            resource_id = str(uuid.uuid4())
            client = Oauth2Client.initialize_with_code(
                "yTB1nwnyQI",
                "07UD2oJtlaJmBxb53KL7",
                oauth2_code,
                "http://127.0.0.1:8000/oauth/",
                resource_id,
                cache,
                token_endpoint_url="https://wenet.u-hopper.com/dev/api/oauth2/token"
            )
            service_api_interface = ServiceApiInterface(client, platform_url="https://wenet.u-hopper.com/dev")
            token_details = service_api_interface.get_token_details()
            user_profile = service_api_interface.get_user_profile(token_details.profile_id)
            request.session['has_logged'] = True
            request.session['resource_id'] = resource_id
            return HttpResponse(f"<html><body>Hi {user_profile.name.first}. <a href='/survey'>here</a> you can take your survey. <a href='/logout'>here</a> you can log out from the app.</body></html>")
        except Exception as e:
            logger.exception("Something went wrong during the login operation", exc_info=e)
            return HttpResponseServerError("<html><body>Something went wrong during the login operation.</body></html>")
