from __future__ import absolute_import, annotations

import logging

from django.conf import settings
from wenet.interface.client import Oauth2Client
from wenet.interface.exceptions import RefreshTokenExpiredError
from wenet.interface.service_api import ServiceApiInterface
from wenet.model.user.common import Gender

from common.cache import DjangoCacheCredentials
from common.rules import RuleManager, BirtDateRule, GenderRule
from wenet_survey.celery import app
from ws.models.survey import SurveyAnswer


logger = logging.getLogger("wenet-survey-web-app.common.tasks")


class CeleryTask:

    @staticmethod
    def update_user_profile(survey_answer: SurveyAnswer) -> None:
        update_user_profile.delay(survey_answer.to_repr())


@app.task()
def update_user_profile(raw_survey_answer: dict):
    survey_answer = SurveyAnswer.from_repr(raw_survey_answer)
    client = Oauth2Client(
        settings.WENET_APP_ID,
        settings.WENET_APP_SECRET,
        survey_answer.wenet_id,
        DjangoCacheCredentials(),
        token_endpoint_url=f"{settings.WENET_INSTANCE_URL}/api/oauth2/token"
    )
    service_api_interface = ServiceApiInterface(client, platform_url=settings.WENET_INSTANCE_URL)
    try:
        user_profile = service_api_interface.get_user_profile(survey_answer.wenet_id)
        logger.info(f"Original profile: {user_profile}")
        rule_manager = RuleManager([BirtDateRule("A02")])
        gender_mapping = {
            "1": Gender.MALE,
            "2": Gender.FEMALE,
            "3": Gender.OTHER,
            "4": Gender.NON_BINARY,
            "5": Gender.NOT_SAY
        }
        rule_manager.add_rule(GenderRule("A01", gender_mapping))
        user_profile = rule_manager.update_user_profile(user_profile, survey_answer)
        service_api_interface.update_user_profile(user_profile.profile_id, user_profile)
        user_profile = service_api_interface.get_user_profile(survey_answer.wenet_id)
        logger.info(f"Updated profile: {user_profile}")
    except RefreshTokenExpiredError:
        logger.info("Token expired")
    except Exception as e:
        logger.exception("Unexpected error occurs", exc_info=e)
