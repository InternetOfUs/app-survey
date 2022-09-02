from __future__ import absolute_import, annotations

import logging
import time
from datetime import datetime
from typing import Optional

from django.conf import settings
from django.db import transaction
from wenet.interface.client import Oauth2Client
from wenet.interface.exceptions import RefreshTokenExpiredError, AuthenticationException
from wenet.interface.service_api import ServiceApiInterface
from wenet.model.user.common import Gender
from wenet.model.user.profile import WeNetUserProfile

from common.cache import DjangoCacheCredentials
from common.enumerator import AnswerOrder
from common.rules import RuleManager, MappingRule, CompetenceMeaningNumberRule, \
    MaterialsMappingRule, CompetenceMeaningBuilderRule, NumberToDateRule, UniversityFromDepartmentRule
from survey.mappings.nationality_mappings import NATIONALITY_MAPPINGS
from survey.mappings.university_mappings import get_all_department_mapping, get_all_degree_mapping
from tasks.models import FailedProfileUpdateTask, LastUserProfileUpdate
from wenet_survey.celery import app
from ws.models.survey import SurveyAnswer

logger = logging.getLogger("wenet-survey-web-app.tasks.tasks")


class ProfileHandler:

    def __init__(self, profile_id: str):
        self._profile_id = profile_id
        client = Oauth2Client(
            settings.WENET_APP_ID,
            settings.WENET_APP_SECRET,
            profile_id,
            DjangoCacheCredentials(),
            token_endpoint_url=f"{settings.WENET_INSTANCE_URL}/api/oauth2/token"
        )
        self._service_api_interface = ServiceApiInterface(client, platform_url=settings.WENET_INSTANCE_URL)

    def update_profile(self, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        user_profile = self._get_user_profile_from_service_api()
        logger.info(f"Original profile: {user_profile}")

        gender_mapping = {
            "01": Gender.MALE,
            "02": Gender.FEMALE,
            "03": Gender.OTHER,
            "04": Gender.NOT_SAY
        }
        rule_manager = RuleManager([MappingRule("Q01", gender_mapping, "gender")])
        rule_manager.add_rule(NumberToDateRule("Q02", "date_of_birth"))

        univ_flat_mapping = {
            "01": "Hall of residence / dormitory",
            "02": "Private shared accommodation",
            "03": "With family and/or relatives",
            "04": "Other"
        }

        rule_manager.add_rule(MaterialsMappingRule("Q03", "department", get_all_department_mapping(), "university_status"))
        rule_manager.add_rule(MaterialsMappingRule("Q04", "study_year", get_all_degree_mapping(), "university_status"))

        rule_manager.add_rule(UniversityFromDepartmentRule("Q03", "university", "university_status"))

        rule_manager.add_rule(MaterialsMappingRule("Q05", "accommodation", univ_flat_mapping, "university_status"))
        rule_manager.add_rule(MappingRule("Q05a", NATIONALITY_MAPPINGS, "nationality"))

        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06a", "c_food", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06b", "c_eating", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06c", "c_lit", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06d", "c_creatlit", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06e", "c_app_mus", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06f", "c_perf_mus", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06g", "c_plays", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06h", "c_perf_plays", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06i", "c_musgall", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06j", "c_perf_art", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06k", "c_watch_sp", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06l", "c_ind_sp", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06m", "c_team_sp", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06n", "c_accom", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06o", "c_locfac", 5, "interest", "competences"))

        rule_manager.add_rule(CompetenceMeaningNumberRule("Q07a", "u_active", 5, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q07b", "u_read", 5, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q07c", "u_essay", 5, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q07d", "u_org", 5, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q07e", "u_balance", 5, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q07f", "u_assess", 5, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q07g", "u_theory", 5, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q07h", "u_pract", 5, "university_activity", "competences"))

        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08a", "v_support", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08b", "v_success", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08c", "v_sexuality", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08d", "v_know", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08e", "v_emotion", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08f", "v_power", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08g", "v_affect", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08h", "v_relig", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08i", "v_health", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08j", "v_pleasure", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08k", "v_prestige", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08l", "v_obed", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08m", "v_stabil", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08n", "v_belong", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08o", "v_beauty", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08p", "v_trad", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08q", "v_surviv", 5, "guiding_principles", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q08r", "v_mature", 5, "guiding_principles", "meanings"))

        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09a", "p_party", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09b", "p_feel", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09c", "p_chores", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09d", "p_mood", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09e", "p_vivid", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09f", "p_talk", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09g", "p_otherprblm", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09h", "p_place", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09i", "p_relax", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09j", "p_intabs", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09k", "p_tlkparty", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09l", "p_feelem", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09m", "p_order", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09n", "p_upset", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09o", "p_undabs", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09p", "p_back", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09q", "p_intother", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09r", "p_mess", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09s", "p_blue", 5, "big_five", "meanings"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09t", "p_goodim", 5, "big_five", "meanings"))

        excitement_order_mapping = {
            "Q08c": AnswerOrder.NORMAL,
            "Q08e": AnswerOrder.NORMAL,
            "Q08j": AnswerOrder.NORMAL
        }
        rule_manager.add_rule(CompetenceMeaningBuilderRule(excitement_order_mapping, "excitement", 5, "guiding_principles", "meanings"))
        promotion_order_mapping = {
            "Q08b": AnswerOrder.NORMAL,
            "Q08f": AnswerOrder.NORMAL,
            "Q08k": AnswerOrder.NORMAL
        }
        rule_manager.add_rule(CompetenceMeaningBuilderRule(promotion_order_mapping, "promotion", 5, "guiding_principles", "meanings"))
        existence_order_mapping = {
            "Q08i": AnswerOrder.NORMAL,
            "Q08m": AnswerOrder.NORMAL,
            "Q08q": AnswerOrder.NORMAL
        }
        rule_manager.add_rule(CompetenceMeaningBuilderRule(existence_order_mapping, "existence", 5, "guiding_principles", "meanings"))
        suprapersonal_order_mapping = {
            "Q08d": AnswerOrder.NORMAL,
            "Q08o": AnswerOrder.NORMAL,
            "Q08r": AnswerOrder.NORMAL
        }
        rule_manager.add_rule(CompetenceMeaningBuilderRule(suprapersonal_order_mapping, "suprapersonal", 5, "guiding_principles", "meanings"))
        interactive_order_mapping = {
            "Q08a": AnswerOrder.NORMAL,
            "Q08g": AnswerOrder.NORMAL,
            "Q08n": AnswerOrder.NORMAL
        }
        rule_manager.add_rule(CompetenceMeaningBuilderRule(interactive_order_mapping, "interactive", 5, "guiding_principles", "meanings"))
        normative_order_mapping = {
            "Q08h": AnswerOrder.NORMAL,
            "Q08l": AnswerOrder.NORMAL,
            "Q08p": AnswerOrder.NORMAL
        }
        rule_manager.add_rule(CompetenceMeaningBuilderRule(normative_order_mapping, "normative", 5, "guiding_principles", "meanings"))

        extraversion_order_mapping = {
            "Q09a": AnswerOrder.NORMAL,  # 1
            "Q09k": AnswerOrder.NORMAL,  # 11
            "Q09f": AnswerOrder.REVERSE,  # 6
            "Q09p": AnswerOrder.REVERSE  # 16
        }
        rule_manager.add_rule(CompetenceMeaningBuilderRule(extraversion_order_mapping, "extraversion", 5, "big_five", "meanings"))
        agreeableness_order_mapping = {
            "Q09b": AnswerOrder.NORMAL,  # 2
            "Q09l": AnswerOrder.NORMAL,  # 12
            "Q09g": AnswerOrder.REVERSE,  # 7
            "Q09q": AnswerOrder.REVERSE  # 17
        }
        rule_manager.add_rule(CompetenceMeaningBuilderRule(agreeableness_order_mapping, "agreeableness", 5, "big_five", "meanings"))
        conscientiousness_order_mapping = {
            "Q09c": AnswerOrder.NORMAL,  # 3
            "Q09m": AnswerOrder.NORMAL,  # 13
            "Q09h": AnswerOrder.REVERSE,  # 8
            "Q09r": AnswerOrder.REVERSE  # 18
        }
        rule_manager.add_rule(CompetenceMeaningBuilderRule(conscientiousness_order_mapping, "conscientiousness", 5, "big_five", "meanings"))
        neuroticism_order_mapping = {
            "Q09d": AnswerOrder.NORMAL,  # 4
            "Q09n": AnswerOrder.NORMAL,  # 14
            "Q09i": AnswerOrder.REVERSE,  # 9
            "Q09s": AnswerOrder.REVERSE  # 19
        }
        rule_manager.add_rule(CompetenceMeaningBuilderRule(neuroticism_order_mapping, "neuroticism", 5, "big_five", "meanings"))
        openness_order_mapping = {
            "Q09e": AnswerOrder.NORMAL,  # 5
            "Q09o": AnswerOrder.REVERSE,  # 15
            "Q09j": AnswerOrder.REVERSE,  # 10
            "Q09t": AnswerOrder.REVERSE  # 20
        }
        rule_manager.add_rule(CompetenceMeaningBuilderRule(openness_order_mapping, "openness", 5, "big_five", "meanings"))

        user_profile = rule_manager.update_user_profile(user_profile, survey_answer)
        logger.debug(f"Before update profile: {user_profile}")
        self._service_api_interface.update_user_profile(user_profile.profile_id, user_profile)  # TODO we should avoid to arrive there without the write feed data permission
        time.sleep(1)
        try:
            self._service_api_interface.update_user_competences(user_profile.profile_id, user_profile.competences)
        except AuthenticationException as e:
            logger.warning(f"Could not update the user {user_profile.profile_id}, server reply with {e.http_status_code}")
        time.sleep(1)
        try:
            self._service_api_interface.update_user_meanings(user_profile.profile_id, user_profile.meanings)
        except AuthenticationException as e:
            logger.warning(f"Could not update the user {user_profile.profile_id}, server reply with {e.http_status_code}")
        time.sleep(1)
        try:
            self._service_api_interface.update_user_materials(user_profile.profile_id, user_profile.materials)
        except AuthenticationException as e:
            logger.warning(f"Could not update the user {user_profile.profile_id}, server reply with {e.http_status_code}")
        time.sleep(1)
        user_profile = self._get_user_profile_from_service_api()
        logger.debug(f"Updated profile: {user_profile}")
        logger.info(f"Completed update for profile: {user_profile.profile_id}")
        return user_profile

    def _get_user_profile_from_service_api(self) -> WeNetUserProfile:
        user_profile = self._service_api_interface.get_user_profile(self._profile_id)
        user_profile.competences = self._service_api_interface.get_user_competences(self._profile_id)
        user_profile.meanings = self._service_api_interface.get_user_meanings(self._profile_id)
        user_profile.materials = self._service_api_interface.get_user_materials(self._profile_id)

        return user_profile


class CeleryTask:

    @staticmethod
    def update_user_profile(survey_answer: SurveyAnswer) -> None:
        update_user_profile.delay(survey_answer.to_repr())


@app.task()
def update_user_profile(raw_survey_answer: dict) -> None:
    survey_answer = SurveyAnswer.from_repr(raw_survey_answer)
    try:
        ProfileHandler(survey_answer.wenet_id).update_profile(survey_answer)

        # create or update LastUserProfileUpdate
        try:
            last_user_profile_update = LastUserProfileUpdate.objects.get(
                wenet_id=survey_answer.wenet_id,
            )
        except LastUserProfileUpdate.DoesNotExist:
            last_user_profile_update = None

        with transaction.atomic():
            if last_user_profile_update is None:
                last_user_profile_update = LastUserProfileUpdate(wenet_id=survey_answer.wenet_id, last_update=datetime.now())
            else:
                last_user_profile_update.last_update = datetime.now()
            last_user_profile_update.save()
    except Exception as e:
        if isinstance(e, RefreshTokenExpiredError):
            logger.warning("Token expired", exc_info=e)
        else:
            logger.exception("Unexpected error occurs", exc_info=e)

        # create or update FailedProfileUpdateTask
        try:
            failed_profile_update_task = FailedProfileUpdateTask.objects.get(
                wenet_id=survey_answer.wenet_id,
            )
        except FailedProfileUpdateTask.DoesNotExist:
            failed_profile_update_task = None

        with transaction.atomic():
            if failed_profile_update_task is None:
                failed_profile_update_task = FailedProfileUpdateTask(wenet_id=survey_answer.wenet_id, raw_survey_answer=raw_survey_answer, failure_datetime=datetime.now())
            else:
                failed_profile_update_task.raw_survey_answer = raw_survey_answer
                failed_profile_update_task.failure_datetime = datetime.now()
            failed_profile_update_task.save()   # TODO say to the user that its profile will be updated soon if an error occurs?


@app.task()
def recover_profile_update_error(raw_survey_answer: dict) -> None:
    survey_answer = SurveyAnswer.from_repr(raw_survey_answer)
    try:
        last_user_profile_update = LastUserProfileUpdate.objects.get(
            wenet_id=survey_answer.wenet_id,
        )
    except LastUserProfileUpdate.DoesNotExist:
        last_user_profile_update = None

    try:
        failed_profile_update_task: Optional[FailedProfileUpdateTask] = FailedProfileUpdateTask.objects.get(
            wenet_id=survey_answer.wenet_id,
        )
    except FailedProfileUpdateTask.DoesNotExist:
        failed_profile_update_task = None

    if last_user_profile_update is not None and failed_profile_update_task is not None and last_user_profile_update.last_update > failed_profile_update_task.failure_datetime:
        logger.info(f"Last profile update is more recent than the failure of the task")
        with transaction.atomic():
            failed_profile_update_task.delete()
    elif failed_profile_update_task is not None and failed_profile_update_task.retry_count >= settings.MAX_RETRY_PROFILE_UPDATE:
        logger.error(f"Profile update task failed {failed_profile_update_task.retry_count} times for {survey_answer.wenet_id}")
        with transaction.atomic():
            failed_profile_update_task.delete()
    elif failed_profile_update_task is not None:
        try:
            ProfileHandler(survey_answer.wenet_id).update_profile(survey_answer)

            # create or update LastUserProfileUpdate
            with transaction.atomic():
                if last_user_profile_update is None:
                    last_user_profile_update = LastUserProfileUpdate(wenet_id=survey_answer.wenet_id, last_update=datetime.now())
                else:
                    last_user_profile_update.last_update = datetime.now()
                last_user_profile_update.save()

            # delete FailedProfileUpdateTask if present
            with transaction.atomic():
                failed_profile_update_task.delete()
        except Exception as e:
            failed_profile_update_task.retry_count += 1
            with transaction.atomic():
                failed_profile_update_task.save()
            if isinstance(e, RefreshTokenExpiredError):
                logger.warning("Token expired", exc_info=e)
            else:
                logger.exception("Unexpected error occurs", exc_info=e)


@app.task()
def recover_profile_update_errors() -> None:
    failed_tasks = FailedProfileUpdateTask.objects.order_by("failure_datetime")
    for failed_task in failed_tasks:
        recover_profile_update_error.delay(failed_task.raw_survey_answer)
