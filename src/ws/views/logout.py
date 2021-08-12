from __future__ import absolute_import, annotations

import logging

from django.http import HttpResponse
from rest_framework.request import Request
from rest_framework.views import APIView


logger = logging.getLogger("wenet-survey-web-app.ws.views.logout")


class LogoutView(APIView):

    def get(self, request: Request):
        request.session['has_logged'] = False
        request.session['resource_id'] = None
        return HttpResponse("<html><body>You logged out.</body></html>")
