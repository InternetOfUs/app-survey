from __future__ import absolute_import, annotations

import logging

from django.http import JsonResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from ws.models.survey import SurveyAnswer
from ws.serializers.survey import SurveyEventSerializer
from tasks.tasks import CeleryTask


logger = logging.getLogger("wenet-survey-web-app.ws.views.survey")


class SurveyEventView(APIView):

    def post(self, request: Request):
        serializer = SurveyEventSerializer(data=request.data)
        if serializer.is_valid():
            try:
                survey_event = serializer.save()
                survey_answer = SurveyAnswer.from_tally(survey_event)
                logger.info(f"Received an answer from user [{survey_answer.wenet_id}] with {len(survey_answer.answers.keys())} answers")
                CeleryTask.update_user_profile(survey_answer)
                return JsonResponse({}, status=status.HTTP_200_OK)
            except ValueError as e:
                logger.exception("Exception in extracting data from the survey event", exc_info=e)
                return JsonResponse({"message": f"Error in extracting data from the survey event: {e}"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception("Exception in extracting data from the survey event", exc_info=e)
                return JsonResponse({"message": f"Error in extracting data from the survey event: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning(serializer.errors)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
