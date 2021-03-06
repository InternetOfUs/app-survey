from __future__ import absolute_import, annotations

import logging
import time
from datetime import datetime

from django.conf import settings
from django.db import transaction
from wenet.interface.client import Oauth2Client
from wenet.interface.exceptions import RefreshTokenExpiredError
from wenet.interface.service_api import ServiceApiInterface
from wenet.model.user.common import Gender
from wenet.model.user.profile import WeNetUserProfile

from common.cache import DjangoCacheCredentials
from common.enumerator import AnswerOrder
from common.rules import RuleManager, MappingRule, CompetenceMeaningNumberRule, \
    MaterialsMappingRule, CompetenceMeaningBuilderRule, NumberToDateRule, UniversityMappingRule
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
        user_profile.competences = service_api_interface.get_user_competences(survey_answer.wenet_id)
        user_profile.meanings = service_api_interface.get_user_meanings(survey_answer.wenet_id)
        user_profile.materials = service_api_interface.get_user_materials(survey_answer.wenet_id)
        logger.info(f"Original profile: {user_profile}")

        gender_mapping = {
            "01": Gender.MALE,
            "02": Gender.FEMALE,
            "03": Gender.OTHER,
            "04": Gender.NOT_SAY
        }
        rule_manager = RuleManager([MappingRule("Q01", gender_mapping, "gender")])
        rule_manager.add_rule(NumberToDateRule("Q02", "date_of_birth"))
        univ_lse_department_mapping = {
            "LSEDEP01": "Department of Accounting",
            "LSEDEP02": "Department of Anthropology",
            "LSEDEP03": "Department of Economics",
            "LSEDEP04": "Department of Economic History",
            "LSEDEP05": "European Institute",
            "LSEDEP06": "Department of Finance",
            "LSEDEP07": "Department of Gender Studies",
            "LSEDEP08": "Department of Geography and Environment",
            "LSEDEP09": "Institute of Global Affairs (IGA)",
            "LSEDEP10": "Department of Government",
            "LSEDEP11": "Department of Health Policy",
            "LSEDEP12": "Department of International Development",
            "LSEDEP13": "Department of International History",
            "LSEDEP14": "International Inequalities Institute",
            "LSEDEP15": "Department of International Relations",
            "LSEDEP16": "Language Centre",
            "LSEDEP17": "Department of Law",
            "LSEDEP18": "Department of Management",
            "LSEDEP19": "Marshall Institute",
            "LSEDEP20": "Department of Mathematics",
            "LSEDEP21": "Department of Media and Communications",
            "LSEDEP22": "Department of Methodology",
            "LSEDEP23": "Department of Philosophy, Logic and Scientific Method",
            "LSEDEP24": "Department of Psychological and Behavioural Science",
            "LSEDEP25": "School of Public Policy",
            "LSEDEP26": "Department of Social Policy",
            "LSEDEP27": "Department of Sociology",
            "LSEDEP28": "Department of Statistics"
        }
        univ_lse_degree_mapping = {
            "LSEDEG01": "Undergraduate year 1",
            "LSEDEG02": "Undergraduate year 2",
            "LSEDEG03": "Undergraduate year 3",
            "LSEDEG04": "Undergraduate year 4",
            "LSEDEG05": "MSc/MA",
            "LSEDEG06": "MPhil/MRes/PhD"
        }
        univ_aau_department_mapping = {
            "AAUDEP01": "City, Dwelling And Settlement (BBB), MSc",
            "AAUDEP02": "Communication (KOM), MA",
            "AAUDEP03": "Communication And Digital Media (KDM), BA",
            "AAUDEP04": "Computer Engineering (CCT), BSc",
            "AAUDEP05": "Construction Management And Informatics (LIB), MSc",
            "AAUDEP06": "Cyber-Security (CS), MSc",
            "AAUDEP07": "Global Refugee Studies - Development and International Relations (GRS), MSc",
            "AAUDEP08": "ICT, Learning and Organizational Change (ILOO), MSc",
            "AAUDEP09": "Information Studies (IS), MSc",
            "AAUDEP10": "Innovative Communication Technologies And Entrepreneurship (ICTE), MSc",
            "AAUDEP11": "Learning And Innovative Change (LFP), MA",
            "AAUDEP12": "Lighting Design (LD), MSc",
            "AAUDEP13": "Medialogy (MED), BSc",
            "AAUDEP14": "Medialogy (MED), MSc",
            "AAUDEP15": "Service Systems Design (SSD), MSc",
            "AAUDEP16": "Social Work (KSA), MSc",
            "AAUDEP17": "Sound And Music Computing (SMC), MSc",
            "AAUDEP18": "Surveying And Planning (SP), MSc",
            "AAUDEP19": "Surveying, Planning And Land Management (LAN), BSc",
            "AAUDEP20": "Surveying, Planning And Land Management (SPLM), MSc",
            "AAUDEP21": "Sustainable Biotechnology, MSc",
            "AAUDEP22": "Sustainable Cities (SusCI), MSc",
            "AAUDEP23": "Sustainable Design (BD), BSc",
            "AAUDEP24": "Sustainable Design (SD), MSc",
            "AAUDEP25": "Techno-anthropology (TAN), BSc",
            "AAUDEP26": "Techno-anthropology (TAN), MSc",
            "AAUDEP27": "Tourism (TUR), MA",
            "AAUDEP28": "Urban, Energy And Environmental Planning (BEM), BSc"
        }
        univ_aau_degree_mapping = {
            "AAUDEG01": "BSc/BA year 1",
            "AAUDEG02": "BSc/BA year 2",
            "AAUDEG03": "BSc/BA year 3",
            "AAUDEG04": "BSc/BA year 4 and beyond",
            "AAUDEG05": "MSc/MA year 1",
            "AAUDEG06": "MSc/MA year 2",
            "AAUDEG07": "PhD",
            "AAUDEG08": "Other"
        }
        univ_unitn_department_mapping = {
            "UNITNDEP01": "CIBIO",
            "UNITNDEP02": "Economics and Management",
            "UNITNDEP03": "Faculty of Law",
            "UNITNDEP04": "Physics",
            "UNITNDEP05": "Civil, Environmental and Mechanical Engineering",
            "UNITNDEP06": "Information Engineering and Computer Science",
            "UNITNDEP07": "Industrial Engineering",
            "UNITNDEP08": "Humanities",
            "UNITNDEP09": "Mathematics",
            "UNITNDEP10": "Psychology and Cognitive Science",
            "UNITNDEP11": "Sociology and Social Research",
            "UNITNDEP12": "Center Agriculture Food Environment",
            "UNITNDEP13": "CIMeC - Centre for Mind/Brain Sciences",
            "UNITNDEP14": "SSI - School of International Studies",
            "UNITNDEP15": "Other structures"
        }
        univ_unitn_degree_mapping = {
            "UNITNDEG01": "Undergraduate year 1",
            "UNITNDEG02": "Undergraduate year 2",
            "UNITNDEG03": "Undergraduate year 3",
            "UNITNDEG04": "Undergraduate year 4",
            "UNITNDEG05": "MSc/MA",
            "UNITNDEG06": "PhD",
            "UNITNDEG07": "Other"
        }
        univ_num_department_mapping = {
            "NUMDEP01": "Business School",
            "NUMDEP02": "School of International Relations and Public Administration",
            "NUMDEP03": "Law School",
            "NUMDEP04": "School of Applied Sciences and Engineering",
            "NUMDEP05": "School of Science - Department of Social Sciences",
            "NUMDEP06": "School of Science - Department of Natural Sciences",
            "NUMDEP07": "School of Science - Department of Humanities",
        }
        univ_num_degree_mapping = {
            "NUMDEG01": "Undergraduate year 1",
            "NUMDEG02": "Undergraduate year 2",
            "NUMDEG03": "Undergraduate year 3",
            "NUMDEG04": "Undergraduate year 4",
            "NUMDEG05": "MSc/MA",
            "NUMDEG06": "PhD",
            "NUMDEG07": "Other"
        }
        univ_uc_department_mapping = {
            "UCDEP01": "Faculty of Accounting, Administrative and Economic Sciences",
            "UCDEP02": "Faculty of science and technology",
            "UCDEP03": "Faculty of Health Sciences",
            "UCDEP04": "Faculty of Legal and Diplomatic Sciences",
            "UCDEP05": "Faculty of Philosophy and Human Sciences"
        }
        univ_uc_degree_mapping = {
            "UCDEG01": "Undergraduate year 1",
            "UCDEG02": "Undergraduate year 2",
            "UCDEG03": "Undergraduate year 3",
            "UCDEG04": "Undergraduate year 4",
            "UCDEG05": "MSc/MA",
            "UCDEG06": "PhD",
            "UCDEG07": "Other"
        }
        univ_flat_mapping = {
            "01": "Hall of residence / dormitory",
            "02": "Private shared accommodation",
            "03": "With family and/or relatives",
            "04": "Other"
        }
        univ_department_mapping = {
            "01": univ_lse_department_mapping,
            "02": univ_aau_department_mapping,
            "03": univ_unitn_department_mapping,
            "04": univ_num_department_mapping,
            "05": univ_uc_department_mapping
        }
        univ_degree_mapping = {
            "01": univ_lse_degree_mapping,
            "02": univ_aau_degree_mapping,
            "03": univ_unitn_degree_mapping,
            "04": univ_num_degree_mapping,
            "05": univ_uc_degree_mapping
        }
        univ_mapping = {
            "01": "LSE",
            "02": "AAU",
            "03": "UNITN",
            "04": "NUM",
            "05": "UC"
        }

        rule_manager.add_rule(UniversityMappingRule("QU", "Q03", "department", univ_department_mapping, "university_status"))
        rule_manager.add_rule(UniversityMappingRule("QU", "Q04", "degree_programme", univ_degree_mapping, "university_status"))

        rule_manager.add_rule(MaterialsMappingRule("QU", "university", univ_mapping, "university_status"))
        rule_manager.add_rule(MaterialsMappingRule("Q05", "accommodation", univ_flat_mapping, "university_status"))

        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06a", "c_food", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06b", "c_eating", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06c", "c_lit", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06d", "c_creatlit", 5, "interest", "competences"))
        rule_manager.add_rule(CompetenceMeaningNumberRule("Q06r", "c_app_mus", 5, "interest", "competences"))
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
        logger.info(f"Before update profile: {user_profile}")
        service_api_interface.update_user_profile(user_profile.profile_id, user_profile)  # TODO we should avoid to arrive there without the write feed data permission
        time.sleep(1)
        service_api_interface.update_user_competences(user_profile.profile_id, user_profile.competences)
        time.sleep(1)
        service_api_interface.update_user_meanings(user_profile.profile_id, user_profile.meanings)
        time.sleep(1)
        service_api_interface.update_user_materials(user_profile.profile_id, user_profile.materials)
        time.sleep(1)
        user_profile = service_api_interface.get_user_profile(survey_answer.wenet_id)
        user_profile.competences = service_api_interface.get_user_competences(survey_answer.wenet_id)
        user_profile.meanings = service_api_interface.get_user_meanings(survey_answer.wenet_id)
        user_profile.materials = service_api_interface.get_user_materials(survey_answer.wenet_id)
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
