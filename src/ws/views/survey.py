from __future__ import absolute_import, annotations

import logging

from rest_framework.request import Request
from rest_framework.views import APIView

from ws.serializers.survey import SurveyEventSerializer


logger = logging.getLogger("wenet-survey-web-app.ws.views.survey")


class SurveyEventsView(APIView):

    def post(self, request: Request):
        print(request.data)
        serializer = SurveyEventSerializer(data=request.data)
        if serializer.is_valid():
            survey_event = serializer.save()
