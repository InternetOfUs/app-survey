from __future__ import absolute_import, annotations

import logging

from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.views import APIView

from ws.serializers.survey import SurveyEventSerializer


logger = logging.getLogger("wenet-survey-web-app.ws.views.survey")


class SurveyEventView(APIView):

    def post(self, request: Request):
        serializer = SurveyEventSerializer(data=request.data)
        if serializer.is_valid():
            survey_event = serializer.save()
            print(survey_event)
        print(serializer.data)
        return JsonResponse(serializer.data)
