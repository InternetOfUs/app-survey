from __future__ import absolute_import, annotations

import logging
from datetime import datetime

from django.conf import settings
from django.db import transaction
from wenet.interface.client import Oauth2Client
from wenet.interface.exceptions import RefreshTokenExpiredError
from wenet.interface.service_api import ServiceApiInterface
from wenet.model.user.common import Gender
from wenet.model.user.profile import WeNetUserProfile

from common.cache import DjangoCacheCredentials
from common.rules import RuleManager, MappingRule, DateRule, CompetenceMeaningNumberRule, CompetenceMeaningMappingRule, \
    MaterialsMappingRule, LanguageRule, MaterialsFieldRule, CompetenceMeaningBuilderRule
from tasks.models import FailedProfileUpdateTask, LastUserProfileUpdate
from wenet_survey.celery import app
from ws.models.survey import SurveyAnswer


logger = logging.getLogger("wenet-survey-web-app.tasks.tasks")


class ProfileHandler:

    @staticmethod
    def update_profile(survey_answer: SurveyAnswer) -> WeNetUserProfile:
        client = Oauth2Client(
            settings.WENET_APP_ID,
            settings.WENET_APP_SECRET,
            survey_answer.wenet_id,
            DjangoCacheCredentials(),
            token_endpoint_url=f"{settings.WENET_INSTANCE_URL}/api/oauth2/token"
        )
        service_api_interface = ServiceApiInterface(client, platform_url=settings.WENET_INSTANCE_URL)
        user_profile = service_api_interface.get_user_profile(survey_answer.wenet_id)
        logger.info(f"Original profile: {user_profile}")
        rule_manager = RuleManager([DateRule("A02", "date_of_birth")])
        gender_mapping = {
            "01": Gender.MALE,
            "02": Gender.FEMALE,
            "03": Gender.OTHER,
            "04": Gender.NON_BINARY,
            "05": Gender.NOT_SAY
        }
        country_mapping = {
            "01": "argentina",
            "02": "australia",
            "03": "austria",
            "04": "belgium",
            "05": "brazil",
            "06": "bulgaria",
            "07": "canada",
            "08": "chile",
            "09": "china",
            "10": "colombia",
            "11": "croatia",
            "12": "czech_republic",
            "13": "denmark",
            "14": "england",
            "15": "estonia",
            "16": "finland",
            "17": "france",
            "18": "germany",
            "19": "greece",
            "20": "hungary",
            "21": "india",
            "22": "ireland",
            "23": "israel",
            "24": "italy",
            "25": "latvia",
            "26": "lithuania",
            "27": "luxembourg",
            "28": "japan",
            "29": "malta",
            "30": "mexico",
            "31": "mongolia",
            "32": "netherlands",
            "33": "new_zeland",
            "34": "norway",
            "35": "paraguai",
            "36": "peru",
            "37": "poland",
            "38": "portugal",
            "39": "cyprus",
            "40": "russia",
            "41": "senegal",
            "42": "slovakia",
            "43": "slovenia",
            "44": "spain",
            "45": "sweden",
            "46": "switzerland",
            "47": "romania",
            "48": "taiwan",
            "49": "thailand",
            "50": "turkey",
            "51": "uk",
            "52": "us",
            "53": "uruguay",
            "54": "venezuela"
        }
        language_name_mapping = {
            "L01": "english",
            "L02": "spanish",
            "L03": "french",
            "L04": "german",
            "L05": "italian",
            "L06": "japanese",
            "L07": "korean",
            "L08": "portuguese",
            "L09": "russian",
            "L10": "chinese"
        }
        linear_2_score_mapping = {
            "01": 0,
            "02": 1
        }
        linear_3_score_mapping = {
            "01": 0,
            "02": 0.5,
            "03": 1
        }
        linear_4_score_mapping = {
            "01": 0,
            "02": 0.33,
            "03": 0.67,
            "04": 1
        }
        linear_5_score_mapping = {
            "01": 0,
            "02": 0.25,
            "03": 0.5,
            "04": 0.75,
            "05": 1
        }

        rule_manager.add_rule(MappingRule("A01", gender_mapping, "gender"))
        rule_manager.add_rule(MappingRule("A03", country_mapping, "nationality"))
        rule_manager.add_rule(LanguageRule("Q07", language_name_mapping, linear_3_score_mapping))

        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09a", "studying", 6, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09b", "cooking", 6, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09c", "literature", 6, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09d", "music", 6, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09r", "arts", 6, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09f", "films", 6, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09g", "physical_exercis", 6, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q09h", "local_facilities", 6, "interest", "competences"))

        rule_manager.add_rule(CompetenceMeaningMappingRule("G01a", "acted_in_theatre", linear_2_score_mapping, "cultural_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("G01b", "sung_in_choir", linear_2_score_mapping, "cultural_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("G01c", "played_instrument", linear_2_score_mapping, "cultural_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("G01d", "played_in_orchestra", linear_2_score_mapping, "cultural_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("G01e", "composed_music", linear_2_score_mapping, "cultural_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("G01f", "danced", linear_2_score_mapping, "cultural_activity", "competences"))

        rule_manager.add_rule(CompetenceMeaningNumberRule("G02a", "theatre_plays", 6, "cultural_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("G02b", "ballets", 6, "cultural_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("G02c", "music_concerts", 6, "cultural_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("G02d", "sports_events", 6, "cultural_activity", "competences"))

        rule_manager.add_rule(CompetenceMeaningNumberRule("G05a", "created_by_hand", 5, "visual_art", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("G05b", "created_visual_arts", 5, "visual_art", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("G05c", "written_literature", 5, "visual_art", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("G05d", "written_blog", 5, "visual_art", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("G07a", "visited_museums", 5, "visual_art", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("G07b", "visited_exhibitions", 5, "visual_art", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("G07c", "visited_monuments", 5, "visual_art", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("G07d", "visited_cinema", 5, "visual_art", "competences"))

        rule_manager.add_rule(CompetenceMeaningMappingRule("G17", "read_books", linear_4_score_mapping, "visual_art", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("C01", "cooking_skill", linear_3_score_mapping, "cooking", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("C04", "cooking_interval", linear_5_score_mapping, "cooking", "competences"))

        rule_manager.add_rule(CompetenceMeaningMappingRule("C07a", "specific_diet", linear_2_score_mapping, "diet", "meanings"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("C07b", "vegan_diet", linear_2_score_mapping, "diet", "meanings"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("C07c", "religious_diet", linear_2_score_mapping, "diet", "meanings"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("C07d", "allergies", linear_2_score_mapping, "diet", "meanings"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("C07e", "healthy_diet", linear_2_score_mapping, "diet", "meanings"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("C07f", "weight_diet", linear_2_score_mapping, "diet", "meanings"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("C07g", "try_new_food", linear_2_score_mapping, "diet", "meanings"))

        rule_manager.add_rule(CompetenceMeaningMappingRule("D03a", "cardio", linear_4_score_mapping, "sport", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("D03b", "aerobics", linear_4_score_mapping, "sport", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("D03c", "water_sports", linear_4_score_mapping, "sport", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("D03d", "weightlifting", linear_4_score_mapping, "sport", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("D03e", "team_sports", linear_4_score_mapping, "sport", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("D03f", "martial_arts", linear_4_score_mapping, "sport", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("D03g", "racket_sports", linear_4_score_mapping, "sport", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("D03h", "recreational", linear_4_score_mapping, "sport", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("D04", "exercise_frequency", linear_4_score_mapping, "sport", "competences"))

        rule_manager.add_rule(CompetenceMeaningNumberRule("C02a", "academic_activities", 6, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("C02b", "take_notes", 6, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("C02c", "arrange_notes", 6, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("C02d", "record_audio", 6, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("C02e", "review_notes", 6, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("C02f", "summarize_books", 6, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("C02g", "course_activities", 6, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("C02h", "special_website_usage", 6, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("C02i", "qa_website_usage", 6, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("C02j", "uni_platform_usage", 6, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("C02k", "edu_platform_usage", 6, "university_activity", "competences"))
        rule_manager.add_rule(CompetenceMeaningMappingRule("A05", "degree", linear_3_score_mapping, "university_status", "competences"))

        univ_flat_mapping = {
            "01": "university students’ dormitory",
            "02": "university flat",
            "03": "university campus",
            "04": "private students’ dormitory",
            "05": "rental house/flat",
            "06": "own/parents/relatives house/apartment",
            "07": "guest of a private person",
            "08": "guest of friend or friends"
        }
        rule_manager.add_rule(MaterialsMappingRule("A11", "accommodation", univ_flat_mapping, "university_status"))
        rule_manager.add_rule(MaterialsFieldRule("A07", "course_year", "university_status"))
        rule_manager.add_rule(MaterialsFieldRule("Q06", "term_postcode", "university_status"))
        rule_manager.add_rule(MaterialsFieldRule("C03", "study_groups", "university_status"))

        linguistic = {
            "B02a": "normal",
            "B02b": "normal",
            "B02c": "normal",
            "B02d": "reverse"
        }
        rule_manager.add_rule(CompetenceMeaningBuilderRule(linguistic, "linguistic", 5, "multiple_intelligence", "competences"))

        user_profile = rule_manager.update_user_profile(user_profile, survey_answer)
        logger.info(f"Before update profile: {user_profile}")
        service_api_interface.update_user_profile(user_profile.profile_id, user_profile)  # TODO we should avoid to arrive there without the write feed data permission
        user_profile = service_api_interface.get_user_profile(survey_answer.wenet_id)
        logger.info(f"Updated profile: {user_profile}")
        return user_profile


class CeleryTask:

    @staticmethod
    def update_user_profile(survey_answer: SurveyAnswer) -> None:
        update_user_profile.delay(survey_answer.to_repr())


@app.task()
def update_user_profile(raw_survey_answer: dict) -> None:
    survey_answer = SurveyAnswer.from_repr(raw_survey_answer)
    try:
        ProfileHandler.update_profile(survey_answer)

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
        failed_profile_update_task = FailedProfileUpdateTask.objects.get(
            wenet_id=survey_answer.wenet_id,
        )
    except FailedProfileUpdateTask.DoesNotExist:
        failed_profile_update_task = None

    if last_user_profile_update is not None and failed_profile_update_task is not None and last_user_profile_update.last_update > failed_profile_update_task.failure_datetime:
        logger.info(f"Last profile update is more recent than the failure of the task")
        with transaction.atomic():
            failed_profile_update_task.delete()
    elif failed_profile_update_task is not None:
        try:
            ProfileHandler.update_profile(survey_answer)

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
            if isinstance(e, RefreshTokenExpiredError):
                logger.warning("Token expired", exc_info=e)
            else:
                logger.exception("Unexpected error occurs", exc_info=e)


@app.task()
def recover_profile_update_errors() -> None:
    failed_tasks = FailedProfileUpdateTask.objects.order_by("failure_datetime")
    for failed_task in failed_tasks:
        recover_profile_update_error.delay(failed_task.raw_survey_answer)
