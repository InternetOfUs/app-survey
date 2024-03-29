from __future__ import absolute_import, annotations

from datetime import datetime
from unittest.mock import Mock, patch

from django.db import transaction
from django.test import TestCase
from wenet.interface.exceptions import AuthenticationException, ApiException
from wenet.model.user.profile import WeNetUserProfile

from tasks.models import FailedProfileUpdateTask, LastUserProfileUpdate
from tasks.tasks import ProfileHandler, update_user_profile, recover_profile_update_error
from django.conf import settings
from ws.models.survey import SurveyAnswer, SingleChoiceAnswer


class TestCeleryTask(TestCase):


    def setUp(self) -> None:
        super().setUp()
        self.profile_handler = ProfileHandler("wenetId")
        settings.WENET_APP_ID = ""
        settings.WENET_APP_SECRET = ""
        settings.WENET_INSTANCE_URL = ""

    def test_update_user_profile(self):
        with patch("tasks.tasks.ProfileHandler.update_profile") as mock_update_profile:
            survey_answer = SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")})
            update_user_profile(survey_answer.to_repr())
            mock_update_profile.assert_called_once()
            self.assertEqual(0, len(FailedProfileUpdateTask.objects.all()))
            self.assertEqual(1, len(LastUserProfileUpdate.objects.all()))

    def test_update_user_profile_exception(self):
        with patch("tasks.tasks.ProfileHandler.update_profile") as mock_update_profile:
            mock_update_profile.side_effect = Exception()
            survey_answer = SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")})
            update_user_profile(survey_answer.to_repr())
            mock_update_profile.assert_called_once()
            self.assertEqual(1, len(FailedProfileUpdateTask.objects.all()))
            self.assertEqual(0, len(LastUserProfileUpdate.objects.all()))

    def test_recover_profile_update_error(self):
        with patch("tasks.tasks.ProfileHandler.update_profile") as mock_update_profile:
            with transaction.atomic():
                last_user_profile_update = LastUserProfileUpdate(
                    wenet_id="wenetId",
                    last_update=datetime.now()
                )
                last_user_profile_update.save()

            with transaction.atomic():
                failed_profile_update_task = FailedProfileUpdateTask(
                    wenet_id="wenetId",
                    raw_survey_answer=SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr(),
                    failure_datetime=datetime.now()
                )
                failed_profile_update_task.save()

            recover_profile_update_error(failed_profile_update_task.raw_survey_answer)
            mock_update_profile.assert_called_once()
            self.assertEqual(0, len(FailedProfileUpdateTask.objects.all()))
            self.assertEqual(1, len(LastUserProfileUpdate.objects.all()))

    def test_recover_profile_update_error_exception(self):
        with patch("tasks.tasks.ProfileHandler.update_profile") as mock_update_profile:
            mock_update_profile.side_effect = Exception()
            with transaction.atomic():
                last_user_profile_update = LastUserProfileUpdate(
                    wenet_id="wenetId",
                    last_update=datetime.now()
                )
                last_user_profile_update.save()

            with transaction.atomic():
                failed_profile_update_task = FailedProfileUpdateTask(
                    wenet_id="wenetId",
                    raw_survey_answer=SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr(),
                    failure_datetime=datetime.now()
                )
                failed_profile_update_task.save()

            recover_profile_update_error(failed_profile_update_task.raw_survey_answer)
            mock_update_profile.assert_called_once()
            self.assertEqual(1, len(FailedProfileUpdateTask.objects.all()))
            self.assertEqual(1, len(LastUserProfileUpdate.objects.all()))

    def test_recover_profile_update_error_without_failed_update(self):
        self.profile_handler.update_profile = Mock()
        recover_profile_update_error(SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr())
        self.profile_handler.update_profile.assert_not_called()
        self.assertEqual(0, len(FailedProfileUpdateTask.objects.all()))
        self.assertEqual(0, len(LastUserProfileUpdate.objects.all()))

    def test_recover_profile_update_error_without_profile_update(self):
        with patch("tasks.tasks.ProfileHandler.update_profile") as mock_update_profile:
            with transaction.atomic():
                failed_profile_update_task = FailedProfileUpdateTask(
                    wenet_id="wenetId",
                    raw_survey_answer=SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr(),
                    failure_datetime=datetime.now()
                )
                failed_profile_update_task.save()

            recover_profile_update_error(failed_profile_update_task.raw_survey_answer)
            mock_update_profile.assert_called_once()
            self.assertEqual(0, len(FailedProfileUpdateTask.objects.all()))
            self.assertEqual(1, len(LastUserProfileUpdate.objects.all()))

    def test_recover_profile_update_error_without_profile_update_exception(self):
        with patch("tasks.tasks.ProfileHandler.update_profile") as mock_update_profile:
            mock_update_profile.side_effect = Exception()
            with transaction.atomic():
                failed_profile_update_task = FailedProfileUpdateTask(
                    wenet_id="wenetId",
                    raw_survey_answer=SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr(),
                    failure_datetime=datetime.now()
                )
                failed_profile_update_task.save()

            recover_profile_update_error(failed_profile_update_task.raw_survey_answer)
            mock_update_profile.assert_called_once()
            self.assertEqual(1, len(FailedProfileUpdateTask.objects.all()))
            self.assertEqual(0, len(LastUserProfileUpdate.objects.all()))

    def test_recover_profile_update_error_old(self):
        self.profile_handler.update_profile = Mock()
        with transaction.atomic():
            failed_profile_update_task = FailedProfileUpdateTask(
                wenet_id="wenetId",
                raw_survey_answer=SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr(),
                failure_datetime=datetime.now()
            )
            failed_profile_update_task.save()

        with transaction.atomic():
            last_user_profile_update = LastUserProfileUpdate(
                wenet_id="wenetId",
                last_update=datetime.now()
            )
            last_user_profile_update.save()

        recover_profile_update_error(failed_profile_update_task.raw_survey_answer)
        self.profile_handler.update_profile.assert_not_called()
        self.assertEqual(0, len(FailedProfileUpdateTask.objects.all()))

    def test_update_user_profile_correctly(self):
        with patch("wenet.interface.service_api.ServiceApiInterface.update_user_profile") as mock_update_user_profile:
            with patch("wenet.interface.service_api.ServiceApiInterface.update_user_competences") as mock_update_user_competences:
                with patch("wenet.interface.service_api.ServiceApiInterface.update_user_meanings") as mock_update_user_meanings:
                    with patch("wenet.interface.service_api.ServiceApiInterface.update_user_materials") as mock_update_user_materials:
                        with patch("tasks.tasks.ProfileHandler._get_user_profile_from_service_api") as mock_get_user_profile_from_service_api:

                            mock_get_user_profile_from_service_api.return_value = WeNetUserProfile.empty("wenetId")
                            survey_answer = SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")})
                            ProfileHandler(survey_answer.wenet_id).update_profile(survey_answer)
                            mock_update_user_profile.assert_called_once()
                            mock_update_user_competences.assert_called_once()
                            mock_update_user_meanings.assert_called_once()
                            mock_update_user_materials.assert_called_once()

    def test_update_user_profile_unauthorized_competences(self):
        with patch("wenet.interface.service_api.ServiceApiInterface.update_user_profile") as mock_update_user_profile:
            with patch("wenet.interface.service_api.ServiceApiInterface.update_user_competences") as mock_update_user_competences:
                with patch("wenet.interface.service_api.ServiceApiInterface.update_user_meanings") as mock_update_user_meanings:
                    with patch("wenet.interface.service_api.ServiceApiInterface.update_user_materials") as mock_update_user_materials:
                        with patch("tasks.tasks.ProfileHandler._get_user_profile_from_service_api") as mock_get_user_profile_from_service_api:

                            mock_update_user_competences.side_effect = AuthenticationException(403, "message")

                            mock_get_user_profile_from_service_api.return_value = WeNetUserProfile.empty("wenetId")
                            survey_answer = SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")})
                            ProfileHandler(survey_answer.wenet_id).update_profile(survey_answer)
                            mock_update_user_profile.assert_called_once()
                            mock_update_user_competences.assert_called_once()
                            mock_update_user_meanings.assert_called_once()
                            mock_update_user_materials.assert_called_once()

    def test_update_user_profile_unauthorized_meanings(self):
        with patch("wenet.interface.service_api.ServiceApiInterface.update_user_profile") as mock_update_user_profile:
            with patch("wenet.interface.service_api.ServiceApiInterface.update_user_competences") as mock_update_user_competences:
                with patch("wenet.interface.service_api.ServiceApiInterface.update_user_meanings") as mock_update_user_meanings:
                    with patch("wenet.interface.service_api.ServiceApiInterface.update_user_materials") as mock_update_user_materials:
                        with patch("tasks.tasks.ProfileHandler._get_user_profile_from_service_api") as mock_get_user_profile_from_service_api:

                            mock_update_user_meanings.side_effect = AuthenticationException(403, "message")

                            mock_get_user_profile_from_service_api.return_value = WeNetUserProfile.empty("wenetId")
                            survey_answer = SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")})
                            ProfileHandler(survey_answer.wenet_id).update_profile(survey_answer)
                            mock_update_user_profile.assert_called_once()
                            mock_update_user_competences.assert_called_once()
                            mock_update_user_meanings.assert_called_once()
                            mock_update_user_materials.assert_called_once()

    def test_update_user_profile_unauthorized_materials(self):
        with patch("wenet.interface.service_api.ServiceApiInterface.update_user_profile") as mock_update_user_profile:
            with patch("wenet.interface.service_api.ServiceApiInterface.update_user_competences") as mock_update_user_competences:
                with patch("wenet.interface.service_api.ServiceApiInterface.update_user_meanings") as mock_update_user_meanings:
                    with patch("wenet.interface.service_api.ServiceApiInterface.update_user_materials") as mock_update_user_materials:
                        with patch("tasks.tasks.ProfileHandler._get_user_profile_from_service_api") as mock_get_user_profile_from_service_api:

                            mock_update_user_materials.side_effect = AuthenticationException(403, "message")

                            mock_get_user_profile_from_service_api.return_value = WeNetUserProfile.empty("wenetId")
                            survey_answer = SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")})
                            ProfileHandler(survey_answer.wenet_id).update_profile(survey_answer)
                            mock_update_user_profile.assert_called_once()
                            mock_update_user_competences.assert_called_once()
                            mock_update_user_meanings.assert_called_once()
                            mock_update_user_materials.assert_called_once()

    def test_update_user_profile_failure(self):
        with patch("wenet.interface.service_api.ServiceApiInterface.update_user_profile") as mock_update_user_profile:
            with patch("wenet.interface.service_api.ServiceApiInterface.update_user_competences") as mock_update_user_competences:
                with patch("wenet.interface.service_api.ServiceApiInterface.update_user_meanings") as mock_update_user_meanings:
                    with patch("wenet.interface.service_api.ServiceApiInterface.update_user_materials") as mock_update_user_materials:
                        with patch("tasks.tasks.ProfileHandler._get_user_profile_from_service_api") as mock_get_user_profile_from_service_api:

                            mock_update_user_profile.side_effect = ApiException(500, "message")

                            mock_get_user_profile_from_service_api.return_value = WeNetUserProfile.empty("wenetId")
                            survey_answer = SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")})
                            with self.assertRaises(Exception):
                                ProfileHandler(survey_answer.wenet_id).update_profile(survey_answer)
                            mock_update_user_profile.assert_called_once()
                            mock_update_user_competences.assert_not_called()
                            mock_update_user_meanings.assert_not_called()
                            mock_update_user_materials.assert_not_called()

    def test_update_user_profile_competences_failure(self):
        with patch("wenet.interface.service_api.ServiceApiInterface.update_user_profile") as mock_update_user_profile:
            with patch("wenet.interface.service_api.ServiceApiInterface.update_user_competences") as mock_update_user_competences:
                with patch("wenet.interface.service_api.ServiceApiInterface.update_user_meanings") as mock_update_user_meanings:
                    with patch("wenet.interface.service_api.ServiceApiInterface.update_user_materials") as mock_update_user_materials:
                        with patch("tasks.tasks.ProfileHandler._get_user_profile_from_service_api") as mock_get_user_profile_from_service_api:

                            mock_update_user_competences.side_effect = ApiException(500, "message")

                            mock_get_user_profile_from_service_api.return_value = WeNetUserProfile.empty("wenetId")
                            survey_answer = SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")})
                            with self.assertRaises(Exception):
                                ProfileHandler(survey_answer.wenet_id).update_profile(survey_answer)
                            mock_update_user_profile.assert_called_once()
                            mock_update_user_competences.assert_called_once()
                            mock_update_user_meanings.assert_not_called()
                            mock_update_user_materials.assert_not_called()

    def test_update_user_profile_meanings_failure(self):
        with patch("wenet.interface.service_api.ServiceApiInterface.update_user_profile") as mock_update_user_profile:
            with patch("wenet.interface.service_api.ServiceApiInterface.update_user_competences") as mock_update_user_competences:
                with patch("wenet.interface.service_api.ServiceApiInterface.update_user_meanings") as mock_update_user_meanings:
                    with patch("wenet.interface.service_api.ServiceApiInterface.update_user_materials") as mock_update_user_materials:
                        with patch("tasks.tasks.ProfileHandler._get_user_profile_from_service_api") as mock_get_user_profile_from_service_api:

                            mock_update_user_meanings.side_effect = ApiException(500, "message")

                            mock_get_user_profile_from_service_api.return_value = WeNetUserProfile.empty("wenetId")
                            survey_answer = SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")})
                            with self.assertRaises(Exception):
                                ProfileHandler(survey_answer.wenet_id).update_profile(survey_answer)
                            mock_update_user_profile.assert_called_once()
                            mock_update_user_competences.assert_called_once()
                            mock_update_user_meanings.assert_called_once()
                            mock_update_user_materials.assert_not_called()

    def test_update_user_profile_materials_failure(self):
        with patch("wenet.interface.service_api.ServiceApiInterface.update_user_profile") as mock_update_user_profile:
            with patch("wenet.interface.service_api.ServiceApiInterface.update_user_competences") as mock_update_user_competences:
                with patch("wenet.interface.service_api.ServiceApiInterface.update_user_meanings") as mock_update_user_meanings:
                    with patch("wenet.interface.service_api.ServiceApiInterface.update_user_materials") as mock_update_user_materials:
                        with patch("tasks.tasks.ProfileHandler._get_user_profile_from_service_api") as mock_get_user_profile_from_service_api:

                            mock_update_user_materials.side_effect = ApiException(500, "message")

                            mock_get_user_profile_from_service_api.return_value = WeNetUserProfile.empty("wenetId")
                            survey_answer = SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")})
                            with self.assertRaises(Exception):
                                ProfileHandler(survey_answer.wenet_id).update_profile(survey_answer)
                            mock_update_user_profile.assert_called_once()
                            mock_update_user_competences.assert_called_once()
                            mock_update_user_meanings.assert_called_once()
                            mock_update_user_materials.assert_called_once()

    def test_failed_profile_retry_count(self):
        with patch("tasks.tasks.ProfileHandler.update_profile") as mock_update_profile:
            with transaction.atomic():
                failed_profile_update_task = FailedProfileUpdateTask(
                    wenet_id="wenetId",
                    raw_survey_answer=SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr(),
                    failure_datetime=datetime.now(),
                    retry_count=10
                )
                failed_profile_update_task.save()

            recover_profile_update_error(failed_profile_update_task.raw_survey_answer)
            mock_update_profile.assert_not_called()
            self.assertEqual(0, len(FailedProfileUpdateTask.objects.all()))