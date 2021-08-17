from __future__ import absolute_import, annotations

import logging
import os

from django.shortcuts import redirect
from rest_framework.request import Request
from rest_framework.views import APIView


logger = logging.getLogger("wenet-survey-web-app.authentication.views.logout")


class LogoutView(APIView):

    def get(self, request: Request):
        request.session["has_logged"] = False
        request.session["resource_id"] = None
        request.session["cache"] = None
        return redirect(os.getenv("BASE_PATH"))
