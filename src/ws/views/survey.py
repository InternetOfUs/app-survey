from __future__ import absolute_import, annotations

import logging
import os

from django.shortcuts import redirect, render
from rest_framework.request import Request
from rest_framework.views import APIView
from wenet.interface.client import Oauth2Client
from wenet.interface.exceptions import RefreshTokenExpiredError
from wenet.interface.service_api import ServiceApiInterface

from ws.common.cache import DjangoCache


logger = logging.getLogger("wenet-survey-web-app.ws.views.survey")


class SurveyView(APIView):

    def get(self, request: Request):
        if request.session.get('has_logged', False):
            client = Oauth2Client(
                os.getenv("APP_ID"),
                os.getenv("APP_SECRET"),
                request.session['resource_id'],
                DjangoCache.from_repr(request.session['cache']),
                token_endpoint_url="https://wenet.u-hopper.com/dev/api/oauth2/token"
            )
            service_api_interface = ServiceApiInterface(client, platform_url="https://wenet.u-hopper.com/dev")
            try:
                token_details = service_api_interface.get_token_details()
                user_profile = service_api_interface.get_user_profile(token_details.profile_id)
                context = {'user_first_name': user_profile.name.first}
                return render(request, 'ws/survey.html', context=context)
            except RefreshTokenExpiredError:
                context = {'login_url': f'{os.getenv("INSTANCE")}/hub/frontend/oauth/login?client_id={os.getenv("APP_ID")}'}
                return render(request, 'ws/token_expired.html', context=context)
        else:
            return redirect(os.getenv("BASE_PATH"))
