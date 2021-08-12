from __future__ import absolute_import, annotations

import logging

from django.http import HttpResponse
from rest_framework.request import Request
from rest_framework.views import APIView
from wenet.interface.client import Oauth2Client
from wenet.interface.service_api import ServiceApiInterface

from ws.common.cache import cache


logger = logging.getLogger("wenet-survey-web-app.ws.views.survey")


class SurveyView(APIView):

    def get(self, request: Request):
        if request.session.get('has_logged', False):
            client = Oauth2Client(
                "yTB1nwnyQI",
                "07UD2oJtlaJmBxb53KL7",
                request.session['resource_id'],
                cache,
                token_endpoint_url="https://wenet.u-hopper.com/dev/api/oauth2/token"
            )
            service_api_interface = ServiceApiInterface(client, platform_url="https://wenet.u-hopper.com/dev")
            token_details = service_api_interface.get_token_details()
            user_profile = service_api_interface.get_user_profile(token_details.profile_id)
            return HttpResponse(f"<html><body>Hi {user_profile.name.first}. This is the Survey page.</body></html>")
        else:
            return HttpResponse(f"<html><body>You are not logged, log <a href='http://wenet.u-hopper.com/dev/hub/frontend/oauth/login?client_id=yTB1nwnyQI'>here</a>.</body></html>")
